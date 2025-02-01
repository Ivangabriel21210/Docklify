# Docklify 🐳🚀

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-24.0%2B-blue?logo=docker)](https://docker.com)

**¡Crea VPS temporales con Docker en 1 clic!**  
*Para desarrolladores, pentesters y curiosos del DevOps.*

## 📌 Descripción
Docklify es una plataforma innovadora que permite crear VPS temporales con solo un clic, usando tecnología Docker. Perfecto para:

- 🔍 Probar configuraciones rápidamente
- 🧪 Experimentar con entornos Linux
- 🚀 Aprender sobre contenedores y DevOps

💻 Desarrollo web temporal
![](static/screenshot.png)

## ✨ Features
- 🕒 VPS Ubuntu 24.04 temporal (1h) o persistente (con registro)
- 🖥️ Terminal web interactiva (ttyd)
- 🔐 Autenticación opcional
- 🧹 Limpieza automática de contenedores
- 🚫 Sin configuración compleja
- 🔄 Persistencia de sesiones
- 🛡️ Aislamiento seguro con Docker
- 🎨 Interfaz moderna y responsive

## 🚀 Instalación
```bash
git clone https://github.com/Ivangabriel21210/Docklify.git
cd Docklify

# Instalar dependencias
pip install -r requirements.txt

# Configurar Docker
sudo usermod -aG docker $USER && newgrp docker

# Iniciar
python3 app.py
```

## 🤝 Contribuir
¡Todas las contribuciones son bienvenidas! Algunas ideas:

- ✅ Mejorar sistema de autenticación

- ✨ Añadir panel de monitoreo

- 🛡️ Implementar HTTPS

- 📁 Sistema de archivos web
