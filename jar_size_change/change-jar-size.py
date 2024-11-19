import zipfile
import os


def adjust_jar_size(jar_path, target_size):
    filler_file_name = "filler.txt"
    temp_jar_path = "temp.jar"

    # Get the current size of the JAR
    current_size = os.path.getsize(jar_path)

    # Calculate how much padding we need
    padding_size = target_size - current_size
    if padding_size <= 0:
        print("Target size is less than or equal to current size. No adjustment needed.")
        return

    print(f"Current size: {current_size} bytes")
    print(f"Target size: {target_size} bytes")
    print(f"Padding size needed: {padding_size} bytes")

    # Create a filler text file
    with open(filler_file_name, "w") as filler_file:
        filler_file.write("A" * padding_size)

    # Add the filler file to the JAR
    with zipfile.ZipFile(jar_path, 'a') as jar:
        jar.write(filler_file_name, filler_file_name)

    # Remove the temporary filler file
    os.remove(filler_file_name)

    # Verify the new size
    new_size = os.path.getsize(jar_path)
    if new_size == target_size:
        print(f"JAR successfully adjusted to target size: {new_size} bytes")
    else:
        print(f"Failed to achieve the exact target size. Current size: {new_size} bytes")


# Example usage
jar_path = "example.jar"  # Replace with your JAR file path
target_size = 13593801  # Replace with your target file size
adjust_jar_size(jar_path, target_size)
