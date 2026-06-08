import csv

from sqlalchemy.orm import Session

from src.db.models import engine, init_db, Fact


def seed(csv_path: str = "data/facts.csv"):
	init_db()
	with Session(engine) as s, open(csv_path) as f:
		reader = csv.DictReader(f)
		for row in reader:
			s.add(Fact(**row))
		s.commit()
	print("Seed complete.")


if __name__ == "__main__":
	seed()
