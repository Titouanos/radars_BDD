import csv

with open('radars_final.csv', 'r', encoding='latin-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    headers = reader.fieldnames
    
    print(f'Nombre de colonnes: {len(headers)}')
    print('\nHeaders détaillés:')
    for i, h in enumerate(headers):
        print(f'  {i}: [{h}] (longueur={len(h)}, repr={repr(h)})')
    
    # Lire première ligne
    row = next(reader)
    print('\nPremière ligne:')
    for key, val in row.items():
        print(f'  [{key}]: "{val}"')
