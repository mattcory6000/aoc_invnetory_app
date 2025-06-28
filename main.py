from app import create_app

print("Creating app...")  # debug line
app = create_app()
print("App created. Starting server...")  # debug line

if __name__ == '__main__':
    app.run(debug=True)