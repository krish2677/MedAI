import logging
import os

try:
    import kagglehub
except ImportError:
    print("Please install kagglehub: pip install kagglehub")
    exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def download_medical_datasets():
    logger.info("🚀 Starting download of medical AI training datasets.")
    logger.warning("⚠️ WARNING: These datasets are massive (100GB+ combined). Ensure you have enough disk space and a stable internet connection.")
    
    print("\n" + "="*50)
    print("1. CHEST X-RAY DATASETS")
    print("="*50)
    logger.info("Downloading NIH Chest X-rays (14 diseases)...")
    path_nih = kagglehub.dataset_download("nih-chest-xrays/data")
    logger.info(f"✅ NIH Chest X-rays saved to: {path_nih}")
    
    logger.info("Downloading COVID-19 Radiography Database...")
    path_covid = kagglehub.dataset_download("tawsifurrahman/covid19-radiography-database")
    logger.info(f"✅ COVID-19 dataset saved to: {path_covid}")
    
    print("\n" + "="*50)
    print("2. SKIN LESION DATASETS")
    print("="*50)
    logger.info("Downloading HAM10000 Skin Cancer MNIST...")
    path_skin = kagglehub.dataset_download("kmader/skin-cancer-mnist-ham10000")
    logger.info(f"✅ Skin Lesion dataset saved to: {path_skin}")
    
    print("\n" + "="*50)
    print("3. RETINAL SCAN DATASETS")
    print("="*50)
    logger.info("Downloading Ocular Disease Recognition (ODIR-5K)...")
    path_retina = kagglehub.dataset_download("andrewmvd/ocular-disease-recognition-odir5k")
    logger.info(f"✅ Retinal dataset saved to: {path_retina}")
    
    print("\n" + "="*50)
    logger.info("🎉 All standard medical datasets downloaded successfully!")
    logger.info("Next steps: Write a PyTorch training loop (train.py) pointing to these folders to fine-tune your EfficientNet models.")

if __name__ == "__main__":
    # Ensure kagglehub is authenticated.
    # Note: You may need to set KAGGLE_USERNAME and KAGGLE_KEY in your environment variables,
    # or have a kaggle.json file in ~/.kaggle/ for this to work depending on the dataset requirements.
    download_medical_datasets()
