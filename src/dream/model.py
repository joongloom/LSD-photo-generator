import tensorflow as tf
import random

class DreamModel:
    def __init__(self):
        # Загружаем базовую модель один раз
        self.base_model = tf.keras.applications.InceptionV3(include_top=False, weights='imagenet')
        self.all_mixed_layers = [f'mixed{i}' for i in range(11)]

    def get_extractor(self, layers):
        """Создает модель для извлечения признаков на основе выбранных слоев."""
        outputs = [self.base_model.get_layer(name).output for name in layers]
        return tf.keras.Model(inputs=self.base_model.input, outputs=outputs)