
#!/bin/bash

server(){
    gunicorn --worker-class eventlet --log-level debug -b 0.0.0.0:5000 app.app:app --reload             
}


database() {
    docker rm -f postgresql_dev
    docker-compose up -d
    sleep 10
    alembic upgrade head
}

deploy_to_docker(){
    echo 'Building...'
    docker build --tag auth_service .
    echo 'Running...'
    docker run --detach -p 5000:5000 auth_service
}


$1