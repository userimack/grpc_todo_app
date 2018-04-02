# grpc_todo_app

To Compile protos/todo.proto file after changes
Use the following command from project root -

    python -m grpc_tools.protoc -I./protos --python_out=./generated_code --grpc_python_out=./generated_code ./protos/todo.proto

Then in the generated_code/todo_pb2_grpc.py file modify the following line

    import todo_pb2 as todo__pb2

to

    from generated_code import todo_pb2 as todo__pb2


To autogenerate migrations use below commands after proper setup:

    alembic revision --autogenerate -m "<Message>"

To apply the changes

    alembic upgrade head

# To generate coverage report use the following command

    py.test --cov=.               \
            --cov-report=annotate \
            --cov-report=html     \
            --cov-report=term     \
            --cov-report=xml

