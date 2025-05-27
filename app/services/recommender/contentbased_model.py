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

df_courses = pd.read_csv(
    Path(__file__).parent.parent.parent.parent / "ml_model" / "content_based" / "udemy_courses_new.csv"
)

class CourseModel(keras.Model):
    def __init__(self, embedding_dim, subject_vocab, level_vocab, course_ids):
        super().__init__()

        # 🔍 Embedding untuk course_id (mengubah ID jadi vektor numerik)
        self.course_embedding = tf.keras.Sequential([
            tf.keras.layers.StringLookup(vocabulary=course_ids, mask_token=None),
            tf.keras.layers.Embedding(len(course_ids) + 1, embedding_dim)
        ])

        # 🎓 Embedding untuk subject course (kategori mata pelajaran)
        self.subject_embedding = tf.keras.Sequential([
            tf.keras.layers.StringLookup(vocabulary=subject_vocab, mask_token=None),
            tf.keras.layers.Embedding(len(subject_vocab) + 1, max(4, embedding_dim // 4))
        ])

        # 🏷️ Embedding untuk level course (pemula, menengah, dsb)
        self.level_embedding = tf.keras.Sequential([
            tf.keras.layers.StringLookup(vocabulary=level_vocab, mask_token=None),
            tf.keras.layers.Embedding(len(level_vocab) + 1, max(2, embedding_dim // 8))
        ])

        # ✍️ Vektorisasi teks judul course dengan TF-IDF dan dense layer
        self.title_vectorizer = tf.keras.layers.TextVectorization(max_tokens=1000, output_mode='tf-idf')
        self.title_vectorizer.adapt(df_courses["course_title"].astype(str).tolist())

        self.title_embedding = tf.keras.Sequential([
            self.title_vectorizer,
            tf.keras.layers.Dense(embedding_dim, activation="relu"),
        ])

        # 📊 Dense layer untuk fitur numerik seperti harga, jumlah subscriber, dll
        self.numerical_dense = tf.keras.Sequential([
            tf.keras.layers.Dense(embedding_dim // 4, activation="relu"),
            tf.keras.layers.Dense(embedding_dim // 8, activation="relu"),
        ])

        # 🔗 Gabungkan semua embedding lalu proses dengan dense layers
        self.final_dense1 = tf.keras.layers.Dense(embedding_dim * 2, activation="relu")
        self.final_dense2 = tf.keras.layers.Dense(embedding_dim)

    def call(self, inputs):
        title = inputs["course_title"]

        # Gabungkan fitur numerik dalam satu tensor
        numerical = tf.stack([
            inputs["price"],
            inputs["num_subscribers"],
            inputs["num_reviews"],
            inputs["num_lectures"],
            inputs["content_duration"],
        ], axis=1)

        # Dapatkan embedding masing-masing fitur
        course_emb = self.course_embedding(inputs["course_id"])
        subject_emb = self.subject_embedding(inputs["subject"])
        level_emb = self.level_embedding(inputs["level"])
        title_emb = self.title_embedding(title)
        numerical_emb = self.numerical_dense(numerical)

        # ⚡ Concatenate semua embedding jadi satu vector feature
        concat = tf.concat([course_emb, subject_emb, level_emb, title_emb, numerical_emb], axis=1)

        x = self.final_dense1(concat)
        return self.final_dense2(x)  # Output embedding final untuk course

# Function untuk Membuat dataset TensorFlow train & test
def make_tf_dataset(df, shuffle=True, batch_size=64):
    ds = tf.data.Dataset.from_tensor_slices({
        "course_id": df["course_id"].astype(str).values,
        "course_title": df["course_title"].astype(str).values.reshape(-1),
        "subject": df["subject"].astype(str).values,
        "level": df["level"].astype(str).values,
        "price": df["price"].astype("float32").values,
        "num_subscribers": df["num_subscribers"].astype("float32").values,
        "num_reviews": df["num_reviews"].astype("float32").values,
        "num_lectures": df["num_lectures"].astype("float32").values,
        "content_duration": df["content_duration"].astype("float32").values,
    })
    if shuffle:
        ds = ds.shuffle(1000)
    ds = ds.batch(batch_size).cache().prefetch(tf.data.AUTOTUNE)
    return ds

class ContentBasedModel:
    """
    A class to represent a content-based recommendation model.
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
        model_dir = Path(__file__).parent.parent.parent.parent / "ml_model" / "content_based"
        if model_dir.exists():
            with open(model_dir / "course_ids.pkl", "rb") as f:
                loaded_course_ids = pickle.load(f)
            with open(model_dir / "subject_vocab.pkl", "rb") as f:
                loaded_subject_vocab = pickle.load(f)
            with open(model_dir / "level_vocab.pkl", "rb") as f:
                loaded_level_vocab = pickle.load(f)
                
            loaded_model = CourseModel(
                embedding_dim=64,  # match the embedding_dim used during training
                subject_vocab=loaded_subject_vocab,  # load subject vocab from the saved file
                level_vocab=loaded_level_vocab,  # load level vocab from the saved file
                course_ids=loaded_course_ids  # load course IDs from the saved file
            )
            
            # Compile the loaded model as done during training
            loaded_model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0008901416500660483))
            
            # Call the model with dummy input to initialize variables
            dummy_input = {
                "course_id": tf.constant(["dummy_course"]),
                "course_title": tf.constant(["dummy_title"]),
                "subject": tf.constant(["dummy_subject"]),
                "level": tf.constant(["dummy_level"]),
                "price": tf.constant([0.0], dtype=tf.float32),
                "num_subscribers": tf.constant([0.0], dtype=tf.float32),
                "num_reviews": tf.constant([0.0], dtype=tf.float32),
                "num_lectures": tf.constant([0.0], dtype=tf.float32),
                "content_duration": tf.constant([0.0], dtype=tf.float32),
            }
            loaded_model(dummy_input)

            # Load the model weights
            loaded_model.load_weights(model_dir / "model_weights" / "model_weights")
            
            tf_all_courses = make_tf_dataset(df_courses, batch_size=64, shuffle=False)
            
            loaded_index = tfrs.layers.factorized_top_k.BruteForce(loaded_model)
            loaded_index.index_from_dataset(
                tf_all_courses.map(lambda x: (x["course_id"], loaded_model(x)))
            )
            
            self.model = loaded_index

        else:
            raise FileNotFoundError(f"Model directory {model_dir} does not exist. Please ensure the model is saved correctly.")
        
    def get_model(self):
        """
        Get the content-based recommendation model.
        
        Returns:
            The content-based recommendation model.
        """
        return self.model
    
    def get_recommendations_by_course_id(self, course_id, n):
        # Check if course_id is valid
        if not isinstance(course_id, int):
            raise ValueError("course_id must be an integer.")
        
        # Check if course_id exists in the database
        course = Course.query.filter_by(course_id=course_id).first()
        if not course:
            raise ValueError(f"Course with ID {course_id} does not exist.")
        
        # Get the model
        model = self.get_model()
        
        # Prepare the input for the model
        query_features = {
            "course_id": tf.constant([str(course.course_id)]),
            "course_title": tf.constant([course.course_title]),
            "subject": tf.constant([course.subject]),
            "level": tf.constant([course.level]),
            "price": tf.constant([course.price], dtype=tf.float32),
            "num_subscribers": tf.constant([course.num_subscribers], dtype=tf.float32),
            "num_reviews": tf.constant([course.num_reviews], dtype=tf.float32),
            "num_lectures": tf.constant([course.num_lectures], dtype=tf.float32),
            "content_duration": tf.constant([course.content_duration], dtype=tf.float32),
        }
        
        # Get recommendations from the model
        scores, ids = model(query_features, k=n)
        
        recommendations = []

        recommended_ids = [id.numpy().decode('utf-8') for id in ids[0]]

        recommended_courses = Course.query.filter(Course.course_id.in_(recommended_ids)).all()
        recommendations = [course.to_dict() for course in recommended_courses]

        return recommendations

