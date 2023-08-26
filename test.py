import subprocess
import os

def test_main():
    # Define the inputs
    inputs = "Test\nlocalhost\n5432\nufuktogay\n1234\npoker_tournaments\n".encode('utf-8')
    
    # Run main.py and provide the inputs
    process = subprocess.Popen(['python', 'main.py'], 
                               stdin=subprocess.PIPE, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate(input=inputs)
    
    # Check for errors
    assert process.returncode == 0, f"Error: {stderr.decode('utf-8')}"
    
    # Check the outputs
    expected_outputs = [
        "Enter the name of your project:",
        "Please provide database connection details:",
        "Database configuration is set!"
    ]
    
    for output in expected_outputs:
        assert output in stdout.decode('utf-8'), f"Missing output: {output}"
    
    # Check the generated files
    project_path = "projects/Test"
    db_config_path = os.path.join(project_path, "db_config.txt")
    
    assert os.path.exists(project_path), f"Project directory {project_path} not created!"
    assert os.path.exists(db_config_path), f"Database configuration {db_config_path} not created!"
    
    # Optionally, you can further check the content of db_config.txt to ensure it matches the input values.

    print("All tests passed!")

if __name__ == "__main__":
    test_main()
