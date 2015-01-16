import os

import xml.etree.ElementTree as ET
import pprint
import yaml
import args

ns = "http://schemas.microsoft.com/developer/msbuild/2003"

class CsProj:

	def collect(self):

		# collect item groups
		igs = self.r.findall('.//{%s}ItemGroup' % ns)
		self.itemgroup = {}

		for ig in igs:
			for el in ig:
				tag = el.tag.split('}')[1]
				groupd = self.itemgroup.setdefault(tag,{})
				for k,v in el.attrib.items():
					groupd.setdefault(k, []).append(v)

		
		#pprint.pprint(self.itemgroup)
	def dump(self):
		out = yaml.dump(self.itemgroup)
		print out

	def itemgroup(self, gname):
		self.r.findall('.//{%s}ItemGroup/{%s}' % (ns, ns))
	
	def __init__(self, fname):
		self.fname = fname
		self.t = ET.parse(fname)
		self.r = root = self.t.getroot()
		self.collect()
		return

		#os.system("less " + fname)

def do_dump(arg):
	for fname in arg.file:
		p = CsProj(fname)
		p.dump()


def main():
	args.init()
	s = args.sub('dump', do_dump)
	s.arg('file', nargs='+')
	args.parse()

main()