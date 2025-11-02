import tensorflow as tf

class DreamModel:
    def __init__(self):
        print("загрузка модели...")
        self.base_model = tf.keras.applications.InceptionV3(include_top=False, weights='imagenet')
        print("модель загружена")

    def get_extractor(self, layers):
        outputs = [self.base_model.get_layer(name).output for name in layers]
        return tf.keras.Model(inputs=self.base_model.input, outputs=outputs)