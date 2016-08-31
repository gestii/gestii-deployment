# Deployment

Gestiona el proceso de deploy en múltiples repositorios, incluyendose a si mismo

## Instrucciones para instalar y desarrollar

### Requerimentos mínimos

* git
* python 2.7
* python-pip

### Poner a funcionar

* Clonar el repositorio dentro de alguna carpeta
* `pip install -r requirements.txt`
* Configurar al gusto en `conf/settings_development.py` ó `conf/settings_production`
* `python server.py`

Si todo sale bien, ya tienes deployment corriendo.

### Hacer un request

En general esto lo hace github, pero pa'cuando uno se siente con ganas:

* Crea un archivo con el payload a mandar, digamos `payload.json`
* fírmalo: `$ ./sign_payload.py payload.json` recuerda que en las configuraciones el valor de `GITHUB_TOKEN` sea el mismo entre el que firma y quien va a recibir la petición
* haz la petición: `$ curl -X POST --data-binary @payload.json -H "X-Hub-Signature: sha1=<firma>" -H "Content-Type: application/json" <url>`

Si todo sale bien ya deberías haber logrado una petición
