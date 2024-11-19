import zipfile
import os
import shutil


def adjust_jar_size(original_jar_path, target_size):
    # Generate the new JAR path by appending "_modified" to the original file name
    file_dir, file_name = os.path.split(original_jar_path)
    base_name, ext = os.path.splitext(file_name)
    new_jar_path = os.path.join(file_dir, f"{base_name}_modified{ext}")

    filler_file_name = "filler.txt"

    # Copy the original JAR file to a new file
    shutil.copy(original_jar_path, new_jar_path)

    # Get the current size of the new JAR
    current_size = os.path.getsize(new_jar_path)

    # Calculate initial padding size
    padding_size = target_size - current_size
    if padding_size <= 0:
        print("Target size is less than or equal to the current size. No adjustment needed.")
        return

    print(f"Original JAR path: {original_jar_path}")
    print(f"New JAR path: {new_jar_path}")
    print(f"Current size: {current_size} bytes")
    print(f"Target size: {target_size} bytes")

    while current_size != target_size:
        # Adjust padding size based on difference
        padding_size = target_size - current_size

        if padding_size <= 0:
            print("Padding size went negative. Cannot achieve target size.")
            break

        # Create a filler text file with the adjusted padding size
        with open(filler_file_name, "w") as filler_file:
            filler_file.write("A" * padding_size)

        # Add the filler file to the new JAR
        with zipfile.ZipFile(new_jar_path, 'a') as jar:
            jar.write(filler_file_name, filler_file_name)

        # Remove the temporary filler file
        os.remove(filler_file_name)

        # Check the new size
        current_size = os.path.getsize(new_jar_path)
        print(f"Updated size: {current_size} bytes")

        # Break if the size matches
        if current_size == target_size:
            print(f"New JAR successfully adjusted to target size: {current_size} bytes")
            return

    print(f"Failed to achieve the exact target size. Current size: {current_size} bytes")


# Example usage
adjust_jar_size("jxbrowser-7.39.2.jar", 13786342)
