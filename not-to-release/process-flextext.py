import sys, re
import xml.etree.ElementTree as ET

#| 6 | PSTR | posterior converb | VerbForm=ConvPost | VERB | ?*language-specific | preverb |  |


#    <paragraphs>
#      <paragraph guid="1c73b7b7-5e1b-423d-a4a4-e34784f52606">
#        <phrases>
#          <phrase guid="15ec75e8-9096-4cf0-b6f3-77ad41a80702">
#            <item type="segnum" lang="ru">1</item>
#            <words>
#              <word guid="49fb5a48-175a-4d42-ac54-8b1becf6848a">
#                <item type="txt" lang="dar-Latn-fonipa">maħmad</item>
#                <morphemes>
#                  <morph type="stem" guid="d7f713e8-e8cf-11d3-9764-00c04f186933">
#                    <item type="txt" lang="dar-Latn-fonipa">maħmad</item>
#                    <item type="gls" lang="ru">Магомед</item>
#                  </morph>
#                </morphemes>
#              </word>
#            <item type="gls" lang="en">Магомед, послушай, я расскажу тебе одну сказку, мамин, наша бабушка рассказывала.</item>

def merge_ud(surf, lem, l, gls):
	o = ('X', '_')
	if surf.isnumeric():
		return ('NUM', '_')
	if re.match('[,.~!?"»«]+', surf):
		return ('PUNCT', '_')
	if l == []:
		l = [('X', '_')]
	upos = list(set([i[0] for i in l]))
	print('L,GLS,UPOS', l, '|||', gls,'|||',upos, file=sys.stderr)
	if len(upos) == 1:
		up = upos[0].split('!')
		up.sort()
		up = '!'.join(up)
		feats = []
		for i in l:
			if '!' in i[1]: feats += i[1].split('!')
			else: feats.append(i[1])
		feats = list(set(feats))
		feats.sort()
		if up == 'DET!NOUN!PRON!PROPN' or up == 'DET!NOUN!PROPN':
			o = ('NOUN', '|'.join(feats))
			for i in ['я', 'ты', 'сам']:
				if gls.count('=' + i + ',') > 0:
					o = ('PRON', '|'.join(feats))
			for c in 'АЭИОУЯЕЫЁЮБЦДФГХЙКЛМНПРСТВЖЬЗ':
				if gls.count(c) > 0:
					o = ('PROPN', '|'.join(feats))
		else:
			o = (upos[0], '|'.join(feats))
	elif len(upos) == 2:
		if 'ADJ' in upos and 'DET' in upos:
			feats = list(set([l[0][1], l[1][1]]))
			feats.sort()
			o = ('DET', '|'.join(feats))
		
	return o
	
table = {}
for line in open(sys.argv[1]).readlines():
	if line.count('|') != 9:
		continue
	row = [i.strip() for i in line.split('|')]
	gls = row[2]
	upos = row[5]
	ufeat = row[4]
	table[gls] = (upos, ufeat)

#print(table)
#sys.exit(-1)


buf = sys.stdin.read()
root = ET.fromstring(buf);

for ph in root.findall(".//phrase"): 
	idx = 1
	pid = ph.attrib['guid']
	print('# sent_id = %s' % (pid))
	s_gls = ph.findall('./item[@type="gls"]')[0].text
	words = []
	sent = ''
	for w in ph.findall(".//word"):
		surf = w.findall('.//item')[0].text
		morphs = w.findall('.//morph')
		gls = 'Gloss='
		lem = ''
		ud = []
		for m in morphs:
			item_s = m.findall('.//item[@type="txt"]')[0].text
			if item_s:
				item_s = item_s.strip()
				lem += item_s + '-'	
			items_g = m.findall('.//item[@type="gls"]')
			if len(items_g) > 0:
				gls_i = items_g[0].text.strip()
				gls += gls_i + ','	
				for gls_j in gls_i.split(':'):
					if gls_j in table:
						ud.append(table[gls_j])
		lem = lem.replace('--','-').strip('-')
		if lem == '':
			lem = surf
		gls = gls.strip(', \n')
		(upos, ufeats) = merge_ud(surf, lem, ud, gls)
		sent += surf + ' '
		words.append((idx, surf, lem, gls, upos, ufeats))
		idx += 1
	sent = sent.strip()
	print('# text = %s' % (sent))
	print('# text[rus] = %s' % (s_gls))
	for w in words:
		print('%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (w[0], w[1], w[2], w[4], '_', w[5], '_', '_', '_', w[3]))
	print()
	

#print(table, file=sys.stderr)
