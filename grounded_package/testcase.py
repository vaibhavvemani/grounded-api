from text_extraction import load_website

url = input("Enter website URL: ")

splits = load_website(url)

print(splits)
