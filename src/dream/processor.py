import time
import logging
import gc
import csv
from datetime import datetime
from pathlib import Path

import tensorflow as tf
import numpy as np
from PIL import Image

from config import config

logger = logging.getLogger("dream_core")


class DeepDreamProcessor:
    def __init__(self, dream_model):
        self.model_base = dream_model
        self.metrics_file = config.DATA_DIR / "metrics.csv"
        config.DATA_DIR.mkdir(exist_ok=True)

    def _save_metrics(self, duration, intensity, style):
        file_exists = self.metrics_file.exists()
        try:
            with open(self.metrics_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['timestamp', 'duration_sec', 'intensity', 'style'])
                writer.writerow([datetime.now().isoformat(), round(duration, 2), intensity, style])
        except Exception as e:
            logger.error(f"не удалось сохранить метрики: {e}")

    def run_dream(self, input_path, output_path, intensity, style):
        start_time = time.perf_counter()
        logger.info(f"генерация | {style.upper()} | {intensity.upper()}")

        try:
            cfg = config.INTENSITY_CONFIG.get(intensity, config.INTENSITY_CONFIG['medium'])
            layers = config.STYLE_LAYERS.get(style, config.STYLE_LAYERS['trip'])
            
            extractor = self.model_base.get_extractor(layers)

            with Image.open(input_path) as img_raw:
                img_raw = img_raw.convert('RGB')
                if max(img_raw.size) > config.MAX_IMAGE_SIZE:
                    img_raw.thumbnail((config.MAX_IMAGE_SIZE, config.MAX_IMAGE_SIZE), Image.Resampling.LANCZOS)
                img = np.array(img_raw).astype(np.float32)

            img = tf.keras.applications.inception_v3.preprocess_input(img)
            img = tf.convert_to_tensor(img)
            base_shape = tf.shape(img)[:-1]

            for octave in cfg['octaves']:
                new_size = tf.cast(tf.cast(base_shape, tf.float32) * (cfg['scale'] ** octave), tf.int32)
                img = tf.image.resize(img, new_size)

                for _ in range(cfg['steps']):
                    with tf.GradientTape() as tape:
                        tape.watch(img)
                        img_batch = tf.expand_dims(img, axis=0)
                        activations = extractor(img_batch)
                        if len(activations) == 1:
                            activations = [activations]
                        loss = tf.reduce_sum([tf.math.reduce_mean(act) for act in activations])
                    
                    gradients = tape.gradient(loss, img)
                    gradients /= tf.math.reduce_std(gradients) + 1e-8
                    img = img + gradients * 0.01 
                    img = tf.clip_by_value(img, -1, 1)

            img = tf.image.resize(img, base_shape)
            result_arr = (255 * (img.numpy() + 1.0) / 2.0).astype(np.uint8)
            Image.fromarray(result_arr).save(output_path, quality=95)

            duration = time.perf_counter() - start_time
            logger.info(f"готово за {duration:.2f}с")
            self._save_metrics(duration, intensity, style)
            
        except Exception as e:
            logger.error(f"ошибка обработки: {e}", exc_info=True)
            raise
        finally:
            tf.keras.backend.clear_session()
            gc.collect()