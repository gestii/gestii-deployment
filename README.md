# Deployment

Gestiona el proceso de deploy en múltiples repositorios, incluyendose a si mismo

## Instrucciones para instalar y desarrollar

### Requerimentos mínimos

* git
* python 2.7
* python-pip

### Poner a funcionar

* Clonar el repositorio `git clone <url>`, dentro de alguna carpeta (namespace) donde están el resto de los repositorios a deployear, por ejemplo `/repos/deployment`
* `pip install -r requirements.txt`
* Configurar al gusto en `conf/settings_development.py` ó `conf/settings_
* `python server.py`

Si todo sale bien, ya tienes deployment corriendo.
