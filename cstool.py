import os

import xml.etree.ElementTree as ET
import pprint
import yaml
import args
import copy

ns = "http://schemas.microsoft.com/developer/msbuild/2003"

ET.register_namespace('',ns)
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

	
	def __init__(self, fname):
		self.fname = fname
		self.prjroot = os.path.dirname(fname)
		self.t = ET.parse(fname)
		self.r = root = self.t.getroot()
		self.collect()
		return

	def append_to_group(self, gname, attrs) :
		parenthits = self.r.findall('.//{%s}ItemGroup/{%s}%s/..' % (ns, ns, gname), gname) 
		
		print attrs
		print parenthits
		parent = parenthits[0]
		chi = parent.find('{%s}%s' % (ns, gname))
		cl = copy.deepcopy(chi)
		for k,v in attrs.items():
			cl.set(k,v)
		print cl
		
		parent.append(cl)


	def save(self, fname):
		self.t.write(fname, xml_declaration = True,
           encoding = 'utf-8',
           method = 'xml')

		#os.system("less " + fname)

def do_dump(arg):
	for fname in arg.file:
		p = CsProj(fname)
		p.dump()

def do_add(arg):
	prj = arg.file[0]
	css = arg.file[1:]
	print prj, css
	p = CsProj(prj)


	p.append_to_group('Compile', {'Include' : css[0]})

	p.save("c:/t/test.csproj")
def main():
	args.init()
	s = args.sub('dump', do_dump)
	s.arg('file', nargs='+')
	s = args.sub('add', do_add)
	s.arg('file', nargs='+')
	args.parse()

main()