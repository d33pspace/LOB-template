import zipfile
import os
import shutil


def adjust_jar_size(original_jar_path, target_size):
    # Define file paths
    file_dir, file_name = os.path.split(original_jar_path)
    base_name, ext = os.path.splitext(file_name)
    new_jar_path = os.path.join(file_dir, f"{base_name}_modified{ext}")
    filler_file_path = "filler.txt"

    # Delete existing filler.txt or modified JAR file if they exist
    if os.path.exists(filler_file_path):
        os.remove(filler_file_path)

    if os.path.exists(new_jar_path):
        os.remove(new_jar_path)

    # Copy the original JAR file to a new file (ensure the original remains untouched)
    shutil.copy(original_jar_path, new_jar_path)

    # Get the current size of the new JAR
    current_size = os.path.getsize(new_jar_path)
    print(f"Original JAR path: {original_jar_path}")
    print(f"New JAR path: {new_jar_path}")
    print(f"Current size: {current_size} bytes")
    print(f"Target size: {target_size} bytes")

    # Initial padding size (reduce by 100 bytes)
    initial_padding_size = target_size - current_size - 100
    if initial_padding_size > 0:
        # Create filler.txt with the calculated initial padding size
        with open(filler_file_path, "w") as filler_file:
            filler_file.write("A" * initial_padding_size)

        with zipfile.ZipFile(new_jar_path, 'a') as jar:
            # Add filler.txt to the JAR file (it will be added only once)
            jar.write(filler_file_path, "filler.txt")

        current_size = os.path.getsize(new_jar_path)
        print(f"After initial padding: {current_size} bytes")

    # Fine-tune the size by adding 1 byte at a time
    loop_count = 1
    while current_size < target_size:
        # Delete the modified JAR file each time to ensure a fresh start
        if os.path.exists(new_jar_path):
            os.remove(new_jar_path)

        # Copy the original JAR again to start with a clean file
        shutil.copy(original_jar_path, new_jar_path)

        # Overwrite filler.txt with the loop count index and write to it
        with open(filler_file_path, "a") as filler_file:
            filler_file.write(f"{loop_count}")  # Add loop count to the file

        with zipfile.ZipFile(new_jar_path, 'a') as jar:  # 'a' mode to append to the JAR
            # Re-add filler.txt to the JAR file, overwriting previous entries
            jar.write(filler_file_path, "filler.txt")

        # Update the current size of the JAR
        current_size = os.path.getsize(new_jar_path)
        print(f"After adding {loop_count} byte(s): {current_size} bytes")

        # Increment loop count for next iteration
        loop_count += 1

    # Final check
    if current_size == target_size:
        print(f"New JAR successfully adjusted to target size: {current_size} bytes")
    else:
        print(f"Failed to achieve the exact target size. Current size: {current_size} bytes")


# Example usage
adjust_jar_size("jxbrowser-7.39.2.jar", 13786342)
adjust_jar_size("jxbrowser-javafx-7.39.2.jar", 231616)
adjust_jar_size("jxbrowser-swing-7.39.2.jar", 201290)
adjust_jar_size("jxbrowser-win32-7.39.2.jar", 98108945)
