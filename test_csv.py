import csv

count = 0
with open('radars.csv', 'r', encoding='latin-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    print(f"Colonnes: {reader.fieldnames}")
    for row in reader:
        count += 1
        if count == 1:
            print(f"Premier radar: {row}")
        if count >= 10:
            break

print(f"Total lignes lues: {count}")
