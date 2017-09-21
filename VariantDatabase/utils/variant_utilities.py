"""
Various utility functions for processing variant data e.g. create variant hash.


"""
import hashlib

def get_variant_hash(chromosome, pos, ref,alt):
	"""
	Generates a sha256 hash of the variant. Used as promary key in Variant model.

	Input: chromosome, pos, ref,alt - self explanatory

	Output:

	hash_id = The sha256 hash of the chromosome + " " + pos + " " + ref + " " + alt

	Note The space between the 4 inputs. This stops problem of Chr1 12 A G and Chr11 2 A G being same hash e.g. hash(Chr112AG)

	"""

	hash_id = hashlib.sha256(chromosome+" "+pos+" "+ref+" "+alt).hexdigest()

	return hash_id