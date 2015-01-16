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

	def append_to_group(self, gname, lattrs) :
		parenthits = self.r.findall('.//{%s}ItemGroup/{%s}%s/..' % (ns, ns, gname), gname) 
		
		parent = parenthits[0]
		chi = parent.find('{%s}%s' % (ns, gname))

		for attrs in lattrs:
			cl = copy.deepcopy(chi)
			for k,v in attrs.items():
				cl.set(k,v)
			#print cl
			
			parent.append(cl)



	def save(self, fname):
		self.t.write(fname, xml_declaration = True,
			encoding = 'utf-8',
			method = 'xml')

		#os.system("less " + fname)

	def files(self, group = 'Compile'):
		return [os.path.abspath(os.path.join(self.prjroot, f)) for f in 
			self.itemgroup[group]['Include']]

	def simplify(self):
		self.itemgroup['Reference']['Include'] = [p.split(',')[0]
			for p in self.itemgroup['Reference']['Include']]




def do_dump(arg):
	for fname in arg.file:
		p = CsProj(fname)
		p.simplify()
		p.dump()

def copy_group(tgt, src, group):
	srcfiles = src.files(group)
	tgrel = [os.path.relpath(p, tgt.prjroot) for p in srcfiles]
	incs = [{'Include' : f} for f in tgrel]
	tgt.append_to_group(group, incs)

def do_merge(arg):
	tgt = CsProj(arg.file[0])
	src = CsProj(arg.file[1])
	for group in ['Compile', 'ProjectReference', 'None']:
		copy_group(tgt, src, group)

	tgt.simplify()
	tgt.dump()
	tgt.save('c:/t/testmerge.csproj')


def do_add(arg):
	prj = arg.file[0]

	p = CsProj(prj)
	css = arg.file[1:]
	relfiles = [os.path.relpath(os.path.abspath(f), p.prjroot ) for f in css]
	csss = [{'Include' : f} for f in relfiles]

	p.append_to_group('Compile', csss)

	p.save("c:/t/test.csproj")

def main():
	args.init()
	s = args.sub('dump', do_dump)
	s.arg('file', nargs='+')
	s = args.sub('add', do_add)
	s.arg('file', nargs='+')

	s = args.sub('merge', do_merge)
	s.arg('file', nargs='+')

	args.parse()

main()