import argparse
import os
import csv
import json

def script_directory():
  return os.path.dirname(os.path.abspath(__file__))

def parse_arguments():
  parser = argparse.ArgumentParser(description='Manages Opepen drops')
  parser.add_argument('--seed', type=str, help='The block hash of the reveal transaction')
  return parser.parse_args()

script_dir = os.path.dirname(os.path.abspath(__file__))

# Get our ticket and opepen ownership data
def get_owner_tickets():
  file_path = os.path.join(script_directory(), 'data/tickets.csv')
  owner_tickets = {}

  with open(file_path, 'r') as f:
    reader = csv.DictReader(f)

    owner_tickets = {row['address']: {
      'address': row['address'],
      'tickets': int(row['tickets']),
      'opepen_count': int(row['opepen_count']),
      'opepen_tickets': int(row['opepen_tickets']),
      'checks_edition_count': int(row['checks_edition_count']),
      'checks_original_80_count': int(row['checks_original_80_count']),
      'checks_original_40_count': int(row['checks_original_40_count']),
      'checks_original_20_count': int(row['checks_original_20_count']),
      'checks_original_10_count': int(row['checks_original_10_count']),
      'checks_original_5_count': int(row['checks_original_5_count']),
      'checks_original_4_count': int(row['checks_original_4_count']),
      'checks_original_1_count': int(row['checks_original_1_count']),
      'opepens': set(map(int, row['opepens'].split(', '))),
    } for row in reader}

    return owner_tickets

def get_ticket_ranges(owner_tickets):
  owners = {}
  last_range = 0

  for address, owner in owner_tickets.items():
    last_range += int(owner['tickets'])
    owners[address] = last_range

  return owners, last_range

def mark_token_as_used(owner_tickets, address, token):
  owner = owner_tickets[address]
  owner['opepens'].remove(token)
  owner['tickets'] -= 1
  if len(owner['opepens']) == 0: del owner_tickets[address]

def compute_stats(stats, owner, token, set_size):
  address = owner['address']
  stats['winners'].setdefault(address, {
    'opepen_count': owner['opepen_count'],
    'opepen_tickets': owner['opepen_tickets'],
    'tickets': owner['tickets'],
  })
  stats['winners'][address].setdefault('tokens', []).append({
    'set': set_size,
    'token': token,
  })

def filter_set(set_size, token_sets):
  tokens = filter(lambda t:t['set'] == set_size, token_sets)

  return ', '.join(list(map(lambda t:str(t['token']), tokens)))

def save_collection(sets):
  file_path = os.path.join(script_directory(), 'results/sets.json')
  with open(file_path, 'w') as file:
    json.dump(sets, file, indent=2)

  file_path = os.path.join(script_directory(), 'results/tokens.json')
  with open(file_path, 'w') as file:
    tokens = {token: set_info['set'] for set_info in sets for token in set_info['tokens']}
    sorted_tokens = {k: tokens[k] for k in sorted(tokens)}
    json.dump(sorted_tokens, file, indent=2)

def save_stats(stats):
  file_path = os.path.join(script_directory(), 'results/winner_stats.json')
  with open(file_path, 'w') as file:
    json.dump(stats, file, indent=2)

  file_path = os.path.join(script_directory(), 'results/winner_stats.csv')
  with open(file_path, 'w') as file:
    writer = csv.writer(file)
    writer.writerow([
      'winner',
      'tickets',
      'opepen_count',
      'checks_tickets',
      'set40',
      'set20',
      'set10',
      'set5',
      'set4',
      'set1',
    ])

    for address, winner in stats['winners'].items():
      token_sets = winner['tokens']
      writer.writerow([
        address,
        winner['tickets'],
        winner['opepen_count'],
        winner['tickets'] - winner['opepen_tickets'],
        filter_set(40, token_sets),
        filter_set(20, token_sets),
        filter_set(10, token_sets),
        filter_set(5, token_sets),
        filter_set(4, token_sets),
        filter_set(1, token_sets),
      ])
