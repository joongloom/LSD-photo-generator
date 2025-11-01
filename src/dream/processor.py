import tensorflow as tf
import numpy as np
from PIL import Image
import os

class DeepDreamProcessor:
    def __init__(self, dream_model):
        self.model_base = dream_model

    def deprocess(self, img):
        img = 255 * (img + 1.0) / 2.0
        return tf.cast(img, tf.uint8)

    def calc_loss(self, img, model):
        img_batch = tf.expand_dims(img, axis=0)
        layer_activations = model(img_batch)
        if len(layer_activations) == 1:
            layer_activations = [layer_activations]
        losses = [tf.math.reduce_mean(act) for act in layer_activations]
        return tf.reduce_sum(losses)

    def run_dream(self, image_path: str, output_path: str, intensity: str, is_random: bool):
        # 1. Конфигурация
        settings = {
            'low': {'steps': 30, 'scale': 1.2, 'octaves': range(-1, 1)},
            'medium': {'steps': 50, 'scale': 1.3, 'octaves': range(-2, 2)},
            'high': {'steps': 70, 'scale': 1.4, 'octaves': range(-2, 3)}
        }
        cfg = settings.get(intensity, settings['medium'])
        
        layers = self.model_base.all_mixed_layers if is_random else ['mixed3', 'mixed5']
        if is_random:
            layers = random.sample(self.model_base.all_mixed_layers, random.randint(2, 4))
        
        extractor = self.model_base.get_extractor(layers)

        # 2. Загрузка и подготовка
        img_raw = Image.open(image_path).convert('RGB')
        original_shape = img_raw.size # (width, height)
        img = np.array(img_raw).astype(np.float32)
        img = tf.keras.applications.inception_v3.preprocess_input(img)
        img = tf.convert_to_tensor(img)

        # 3. Цикл по октавам (как в ноутбуке)
        base_shape = tf.shape(img)[:-1]
        for octave in cfg['octaves']:
            new_size = tf.cast(tf.cast(base_shape, tf.float32) * (cfg['scale']**octave), tf.int32)
            img = tf.image.resize(img, new_size)

            # Градиентное восхождение
            for step in range(cfg['steps']):
                with tf.GradientTape() as tape:
                    tape.watch(img)
                    loss = self.calc_loss(img, extractor)
                
                gradients = tape.gradient(loss, img)
                gradients /= tf.math.reduce_std(gradients) + 1e-8
                img = img + gradients * 0.01 # step_size
                img = tf.clip_by_value(img, -1, 1)

        # 4. Финализация
        img_final = tf.image.resize(img, base_shape)
        result_array = self.deprocess(img_final).numpy()
        result_img = Image.fromarray(result_array)
        result_img.save(output_path)