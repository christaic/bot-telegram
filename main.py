import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 🔁 Reemplaza esto con el ID real de tu carpeta compartida en Google Drive
FOLDER_ID = "11b0Vb8YEaiMCmSAQ9TQiWWytx0s9t326"

def subir_archivo_a_drive():
    # Credenciales desde variable de entorno
    cred_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if not cred_json:
        print("❌ Variable de entorno GOOGLE_CREDENTIALS_JSON no encontrada")
        return
    
    creds_dict = json.loads(cred_json)
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    
    service = build('drive', 'v3', credentials=creds)

    # Crear un archivo local temporal
    with open("archivo_prueba.txt", "w") as f:
        f.write("¡Hola desde Render!")

    file_metadata = {
        'name': 'archivo_prueba.txt',
        'parents': [FOLDER_ID]  # 👈 Aquí especificamos la carpeta destino
    }
    media = MediaFileUpload('archivo_prueba.txt', mimetype='text/plain')

    archivo = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"✅ Archivo subido con ID: {archivo.get('id')}")

if __name__ == "__main__":
    subir_archivo_a_drive()
