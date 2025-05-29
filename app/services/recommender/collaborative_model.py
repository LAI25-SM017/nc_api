from threading import Lock
from pathlib import Path
import tensorflow as tf
import os
from app.models.course import Course
from app.extensions import db
import pandas as pd
import tensorflow_recommenders as tfrs
from tensorflow import keras
import pickle

# os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
# os.environ['TF_USE_LEGACY_KERAS'] = '1'

# ⬇️ Inherit dari TFRS (TensorFlow Recommenders)
class CourseModel(tfrs.Model):
    def __init__(self, user_vocab, course_vocab, embedding_dim=64):
        super().__init__()

        # ================================
        # Simpan parameter sebagai atribut
        # Penting untuk get_config agar bisa serialisasi dengan benar
        # ================================
        self.user_vocab = user_vocab
        self.course_vocab = course_vocab
        self.embedding_dim = embedding_dim

        # Tambahkan metrik total_loss eksplisit
        self.total_loss_tracker = tf.keras.metrics.Mean(name="total_loss")

        # ================================
        # 🏛 USER TOWER
        # Ubah user_id (string) ➜ index ➜ embedding
        # ================================
        self.user_model = tf.keras.Sequential([
            tf.keras.layers.StringLookup(
                vocabulary=user_vocab,   # daftar semua user_id
                mask_token=None          # tidak pakai token khusus untuk "kosong"
            ),
            tf.keras.layers.Embedding(
                input_dim=len(user_vocab) + 1,
                output_dim=embedding_dim
            )
        ])

        # ================================
        # 🏫 COURSE TOWER
        # Ubah course_id (string) ➜ index ➜ embedding
        # ================================
        self.course_model = tf.keras.Sequential([
            tf.keras.layers.StringLookup(
                vocabulary=course_vocab,
                mask_token=None
            ),
            tf.keras.layers.Embedding(
                input_dim=len(course_vocab) + 1,
                output_dim=embedding_dim
            )
        ])

        # =======================================
        # 🎯 RETRIEVAL TASK (dengan evaluasi Top-K)
        # Tujuannya adalah: buat user dan course relevan
        # saling mendekat di ruang embedding
        # =======================================
        self.task = tfrs.tasks.Retrieval(
            metrics=tfrs.metrics.FactorizedTopK(
                candidates=tf.data.Dataset.from_tensor_slices(course_vocab)
                    .batch(128)
                    .map(self.course_model)  # konversi course_id ➜ embedding
            )
        )

    # ============================================
    # 🚀 call
    # Definisi forward pass model
    # Input: fitur berisi 'user_id' dan 'course_id'
    # Output: embedding vektor untuk user dan course
    # Dipakai saat inference dan saat menyimpan model
    # ============================================
    def call(self, features):
        user_embeddings = self.user_model(features['user_id'])
        course_embeddings = self.course_model(features['course_id'])
        return user_embeddings, course_embeddings

    # ============================================
    # ⚙️ get_config
    # Mengembalikan konfigurasi model dalam bentuk dictionary
    # Konfigurasi ini berisi parameter penting untuk membangun ulang model
    # Berguna untuk menyimpan dan memuat model subclass dengan benar
    # ============================================
    def get_config(self):
        return {
            'user_vocab': self.user_vocab,
            'course_vocab': self.course_vocab,
            'embedding_dim': self.embedding_dim
        }

    # ============================================
    # 🏗️ from_config (classmethod)
    # Membuat instance model baru dari konfigurasi yang disimpan
    # Memungkinkan reconstruct model dengan parameter yang sama saat loading
    # ============================================
    @classmethod
    def from_config(cls, config):
        return cls(**config)

    # ============================================
    # 🔁 compute_loss
    # Fungsi utama saat training untuk menghitung loss
    # input = features['user_id'] dan ['course_id']
    # output = loss dari user-course pairs
    # ============================================
    def compute_loss(self, features, training=False):
        user_embeddings = self.user_model(features['user_id'])
        course_embeddings = self.course_model(features['course_id'])
        loss = self.task(user_embeddings, course_embeddings)
        self.total_loss_tracker.update_state(loss)
        return loss

    # ============================================
    # 📊 metrics
    # properti agar total_loss dikenali sebagai metrik oleh callback dan bisa di-iterasi oleh Keras
    # ============================================
    @property # Tambahkan dekorator ini!
    def metrics(self):
        # Pastikan ini mengembalikan daftar objek metrik
        # Termasuk metrik dari TFRS task jika kamu ingin juga dimonitor secara langsung oleh Keras
        return [self.total_loss_tracker] + self.task.metrics # self.task.metrics sudah list

class CollaborativeModel:
    """
    A class to represent a colaborative recommendation model.
    """
    _instance = None
    _lock = Lock()
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    
                    # Initialize the model
                    cls._instance._load_model()
        return cls._instance
    
    def _load_model(self):
        """
        Load the content-based recommendation model.
        This is a placeholder for the actual model loading logic.
        """
        
        # Dynamically construct the path to the saved model directory
        model_dir = Path(__file__).parent.parent.parent.parent / "ml_model" / "collaborative"
        if model_dir.exists():
            with open(model_dir / "course_ids.pkl", "rb") as f:
                loaded_course_ids = pickle.load(f)
            with open(model_dir / "user_ids.pkl", "rb") as f:
                loaded_user_ids = pickle.load(f)
                
            loaded_model = CourseModel(
                user_vocab=loaded_user_ids,
                course_vocab=loaded_course_ids,
                embedding_dim=128  # sesuaikan dengan setting waktu training
            )
            
            # Compile model sesuai konfigurasi optimizer awal
            loaded_model.compile(optimizer=tf.keras.optimizers.Adagrad(learning_rate=0.05))
            
            # Load the model weights
            loaded_model.load_weights(model_dir / "model_weights" / "model_weights")
            
            loaded_index = tf.saved_model.load(
                str(model_dir / "saved_cf_index")
            )
            
            # Try 2
            index = tfrs.layers.factorized_top_k.BruteForce(loaded_model.user_model)
            index.index_from_dataset(
                tf.data.Dataset.from_tensor_slices(loaded_course_ids).batch(128).map(lambda cid: (cid, loaded_model.course_model(cid)))
            )
            
            self.model = index

        else:
            raise FileNotFoundError(f"Model directory {model_dir} does not exist. Please ensure the model is saved correctly.")
        
    def get_model(self):
        """
        Get the content-based recommendation model.
        
        Returns:
            The content-based recommendation model.
        """
        return self.model
    
    def get_recommendations_by_user_id(self, user_id, n):
        """
        Get recommendations for a given user ID.
        
        Args:
            user_id (str): The user ID to get recommendations for.
            k (int): The number of recommendations to return.
        
        Returns:
            List of recommended course IDs.
        """
        if not self.model:
            raise ValueError("Model is not loaded. Please initialize the model first.")
        
        model = self.get_model()
        scores, ids = model(tf.constant([user_id]), k=n)
        recommended_course_ids = [cid.numpy().decode() for cid in ids[0]]
        
        # Fetch course details from the database
        recommended_courses = []
        for course_id in recommended_course_ids:
            course = Course.query.filter_by(course_id=course_id).first()
            if course:
                recommended_courses.append(course.to_dict())
        
        return recommended_courses

