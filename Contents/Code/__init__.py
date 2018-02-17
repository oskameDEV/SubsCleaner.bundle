# -*- coding: utf-8 -*-
	#
		#
			# SUBS CLEANER :: AGENT FOR PLEX
				# BY [OK] KITSUNE.WORK - 2018
			# VERSION 0.977
		#
	#
#

# :: IMPORTS ::
from __future__ import with_statement
from __future__ import unicode_literals
import sys
import os
import io
import subprocess
import re
import codecs
import chardet
import urllib
import urllib2
import pipes

####################################################################################################

PLUGIN_VERSION = '0.977'

# :: USER CONFIGURED FILTERS ::
# CLEAN HTML FROM SUBTITLES
removeHTML 		= Prefs['removeHTML']

# REMOVE DASHES IN FRONT OF DIALOGUE. FOR EXAMPLE: "-Please, Izzi."
removeDashes 	= Prefs['removeDashes']

# FIX ALL-CAPS SUBTITLES (MAKES THEM NORMAL CAPITALIZED)
allCaps 		= Prefs['allCaps']

# FIX ALL-CAPS SUBTITLES (MAKES THEM NORMAL CAPITALIZED)
fixCaps 		= Prefs['fixCaps']

# REMOVE MINOR PUNCTUATIONS
remPunc 		= Prefs['remPunc']

# :: TODO :: REMOVE SPECIFIC SYMBOLS FROM SENTENCES :: TODO ::
remSym 			= Prefs['remSym'].split(',')
#remSym 			= remSym.split(',')

# FORCE UTF-8 ENCODING
forceEnc		= Prefs['forceEnc']

# VERBOSE LOGGING
verbLog			= Prefs['verbLog']

# IF FOLLOWING TEXT IS FOUND WITHIN A SUBTITLE, REMOVE SUBTITLE BLOCK
# GOOD AGAINST SPAM OR ADS
# DOMAIN LIST BELOW IS THE BEST WAY TO HAVE THOSE REMOVED, BUT MIGHT VERY RARELY CAUSE A PIECE OF DIALOGUE TO BE REMOVED
# IF YOU WORRY ABOUT THIS JUST ADD A '#' IN FRONT OF THIS LIST TO COMMENT IT OUT
tldFilters 		= ['.film','.movie','.link','.biz','.cat','.com','.edu','.gov','.info','.int','.jobs','.mil','.mobi',
'.name','.net','.org','.ac','.ad','.ae','.af','.ag','.ai','.al','.am','.an','.ao','.aq','.ar','.as','.at','.au','.aw',
'.az','.ba','.bb','.bd','.be','.bf','.bg','.bh','.bi','.bj','.bm','.bn','.bo','.br','.bs','.bt','.bv','.bw','.by','.bz','.ca',
'.cc','.cd','.cf','.cg','.ch','.ci','.ck','.cl','.cm','.cn','.co','.cr','.cs','.cu','.cv','.cx','.cy','.cz','.de','.dj','.dk','.dm',
'.do','.dz','.ec','.ee','.eg','.eh','.er','.es','.et','.eu','.fi','.fj','.fk','.fm','.fo','.fr','.ga','.gb','.gd','.ge','.gf','.gg','.gh',
'.gi','.gl','.gm','.gn','.gp','.gq','.gr','.gs','.gt','.gu','.gw','.gy','.hk','.hm','.hn','.hr','.ht','.hu','.id','.ie','.il','.im',
'.in','.io','.iq','.ir','.is','.it','.je','.jm','.jo','.jp','.ke','.kg','.kh','.ki','.km','.kn','.kp','.kr','.kw','.ky','.kz','.la','.lb',
'.lc','.li','.lk','.lr','.ls','.lt','.lu','.lv','.ly','.ma','.mc','.md','.mg','.mh','.mk','.ml','.mm','.mn','.mo','.mp','.mq',
'.mr','.ms','.mt','.mu','.mv','.mw','.mx','.my','.mz','.na','.nc','.ne','.nf','.ng','.ni','.nl','.no','.np','.nr','.nu',
'.nz','.om','.pa','.pe','.pf','.pg','.ph','.pk','.pl','.pm','.pn','.pr','.ps','.pt','.pw','.py','.qa','.re','.ro','.ru','.rw',
'.sa','.sb','.sc','.sd','.se','.sg','.sh','.si','.sj','.sk','.sl','.sm','.sn','.so','.sr','.st','.su','.sv','.sy','.sz','.tc','.td','.tf',
'.tg','.th','.tj','.tk','.tm','.tn','.to','.tp','.tr','.tt','.tv','.tw','.tz','.ua','.ug','.uk','.um','.us','.uy','.uz', '.va','.vc',
'.ve','.vg','.vi','.vn','.vu','.wf','.ws','.ye','.yt','.yu','.za','.zm','.zr','.zw']

# CUSTOM WORDS THAT WILL MAKE A SUBTITLE BLOCK BE REMOVED
customFilterPref = Prefs['customFilters'].split(',')
customFilters 	 = []
# GO THROUGH EACH AND DECODE ANY THAT HAVE BEEN ENCODED (DUE TO PLEX LIMITATION WITH CHARACTERS)
filtersLog 		 = ''
for kw in customFilterPref:
	filtersLog += urllib2.unquote(kw.encode('ascii'))+', '
	customFilters.append(urllib2.unquote(kw.encode('ascii')))
if verbLog:
	Log.Debug(':: FILTERS :: %s ::', filtersLog)

# REMOVE HEARING IMPAIRED LINES
remHI 				= Prefs['remHI']

# COMBINE LISTS
subFilters 			= tldFilters + customFilters

# :: NOT CONFIGURABLE YET ::
fileTypes 			= ['.srt']

####################################################################################################

def Start():
	Log(':: SUBTITLE CLEANER AGENT LAUNCHED ::')
	# -----------------------------------------------------------------------------|
	# PING THE CREATOR OF THIS AGENT TO RECORD USAGE 							   |
	# NOTHING CREEPY, JUST WANT TO KNOW HOW MUCH TIME TO INVEST 				   |
	# BASED ON HOW MANY PEOPLE USE MY WORK 										   |
	# I HAVE TO USE SOME KIND OF UNIQUE IDENTIFIER TO MAKE SURE STATS ARE ACCURATE |
	# -----------------------------------------------------------------------------|
	ID 	= HTTP.Request('https://plex.tv/pms/:/ip').content
	RNG	= HTTP.Request('http://projects.kitsune.work/aTV/SC/ping.php?ID='+str(ID)).content

####################################################################################################

# :: PLEX AGENT ::
class SubsCleanerAgent(object):
	languages = [Locale.Language.NoLanguage]
	primary_provider = False

	def __init__(self, *args, **kwargs):
		super(SubsCleanerAgent, self).__init__(*args, **kwargs)
		self.agent_type = "MOVIES" if isinstance(self, Agent.Movies) else "SERIES"
		self.name = "SubsCleaner (%s, v%s)" % (self.agent_type_verbose, PLUGIN_VERSION)

	def search(self, results, media, lang):
		Log(':: SUBSCLEANER (%s) STARTED ::' % self.agent_type)
		if media.primary_metadata is not None:
			results.Append(MetadataSearchResult(
				id = media.primary_metadata.id,
				score = 100
			))

	def update(self, results, media, lang):
		# MOVIES
		if self.agent_type is "MOVIES":
			for i in media.items:
				for part in i.parts:
					processFILES(part, 'MOVIE')

		# SERIES
		else:
			for s in media.seasons:
				if int(s) < 1900:
					for e in media.seasons[s].episodes:
						for i in media.seasons[s].episodes[e].items:
							for part in i.parts:
								processFILES(part, 'TV')

####################################################################################################

# PROCESS FILES IN DIRECTORY
def processFILES(part, MTYPE):
	# CURRENT MEDIA
	mediaFile = part.file.decode('utf-8')
	# IT'S DIRECTORY
	mediaDir = os.path.dirname(mediaFile).decode('utf-8')
	for root, dirs, files in os.walk(mediaDir, topdown=False):
		# GO THROUGH EACH FILE IN FOLDER
		for file in files:
			# MAKE SURE IT IS AN ALLOWED FILETYPE
			if '.srt' in str(file):
				# PROCESS EACH SUBTITLE
				cleanSubs(mediaDir, file, MTYPE)

# :: SUBTITLES CLEANER ::
# REMOVE HTML TAGS
def remHTML(HTML):
	rawTEXT 	= re.compile('<.*?>')
	cleanText 	= re.sub(rawTEXT, '', HTML)
	# ALSO REMOVE SUBTITLE STYLE MARKUP?
	return cleanText

# CLEAN SUBTITLE FILE
def cleanSubs(folder, file, MTYPE):
	# LOG INDICATOR BETWEEN FILES FOR EASIER READING
	Log('----------------------------------------------------------------------------------')

	# LOCATION OF FILE
	target   = folder+'/'+file
	enc 	 = 'UTF-8'

	# DETECT .SRT FILE ENCODING
	# try:
	# 	# ASSUME ENCODING BASED ON FILE NAMING
	# 	lang = re.search(r"\.(\w+)\.srt", target)
	# 	lang = lang.group(1)
	# 	if lang:
	# 		# LANGUAGE FOUND BEFORE EXTENTION
	# except:
	# 	lang = None
	try:
		with io.open(target, "rb") as f:
			cnt = f.read()
			enc = chardet.detect(cnt)
			enc = enc['encoding']
	except:
		try:
			enc = subprocess.Popen("file --mime %s" % pipes.quote(target), shell=True, stdout=subprocess.PIPE).stdout.read()
			enc = enc.split('=')
			enc = enc[1].strip()
		except:
			# FALLBACK TO UTF-8
			enc = 'UTF-8'
	# SMALL FIX FOR OLDER VERIONS
	if enc is None:
		enc = 'UTF-8'
	if 'unknown' in enc:
		enc = 'UTF-8'

	# OPEN SUB FILE FOR SCRUBBING
	if verbLog:
		Log.Debug(':: FILE ENCODING :: %s ::', enc)
	try:
		# OPEN TARGET FILE WITH CORRECT ENCODING
		with codecs.open(target, 'rU', encoding=enc, errors='replace') as sourceFile:
			dataRAW	= sourceFile.read()
			data 	= dataRAW.split('\n\n')
			# IF DATA IS ONLY 1 BLOCK, TRY DIFFERENT LINE-ENDINGS TILL SPLIT WORKS
			if len(data) is 1:
				data 	= dataRAW.split('\r\n')
			if len(data) is 1:
				data 	= dataRAW.split(os.linesep + os.linesep)
	except:
		Log('/!\ ERROR READING SUBTITLE FILE :: %s /!\\', target)

	if data and len(data) > 1:
		# RESET VARS FOR EACH FILE
		cleanData 	= ''
		ignored 	= False
		if verbLog:
			Log.Debug(':: TOTAL NUMBER OF SUBTITLE BLOCKS :: %s ::', len(data))

		# PROCESS BLOCK BY BLOCK
		for block in data:
			# PROCESS EVERY LINE
			for line in block.splitlines():
				subLine = line
				# LEAVE INTACT IF LINE IS JUST A NUMBER OR TIMESTAMP
				if (subLine.isdigit()) or (re.match('\d{2}:\d{2}:\d{2}', subLine)):
					cleanData += subLine+'\n'
					# SKIP TO NEXT LINE
				else:
					# REMOVE HTML TAGS FROM SUBTITLE
					if removeHTML:
						subLine = remHTML(subLine)
					# FIX SUBTITLES THAT ARE IN ALL CAPS
					if fixCaps:
						subLine = subLine.capitalize()
					# IF ALL CAPS ENABLED
					if allCaps:
						subLine = subLine.upper()
					# REMOVE HEARING IMPAIRED CAPTIONS
					if remHI:
						subLine =  re.sub("[\(\[].*?[\)\]]", "", subLine)
						# REMOVE FIRST SPACE IF PRESENT
						if subLine[:1] is ' ':
							subLine = subLine[1:]
						else:
							subLine = subLine

					# CHECK IF ANY PART OF THE TEXT IN BLOCK MATCHES FILTER LIST
					# CHECK TO SEE IF SENTENCE IN BLOCK CONTAINS A BLACKLISTED WORD
					for fltr in subFilters:
						# TRY TO DECODE POSSIBLE LANGUAGE SPECIFIC FILTER
						if not ignored:
							if fltr.decode('utf-8').lower() in line.decode('utf-8').lower():
								# EXCEPTIONS
								# BUT NOT WITH .. OR ... DUE TO IT THINKING IT MIGHT BE A LTD/WEBSITE
								if '..' not in line and '...' not in line:
									if verbLog:
										Log.Debug(':: REMOVED {%s} BECAUSE OF {%s} ::', line.upper(), fltr.upper())
									ignored = True # WILL NOT ADD THIS ENTIRE BLOCK
									cleanData += ' \n'

					# ELSE JUST PROCESS NORMALLY AS A SENTENCE
					if not ignored:
						# REMOVE MINOR PUNCTUATIONS
						if remPunc:
							remPuncs = [',','.',':']
							# LOGGIN
							#if ',' in subLine or '.' in subLine or ':' in subLine:
								#if verbLog:
									#Log.Debug(':: REMOVED MINOR PUNCTUATIONS ::')
							for p in remPuncs:
								subLine = subLine.replace(p, '')
						# REMOVE CERTAIN SYMBOLS FROM LINES BUT LEAVE THE REST INTACT
						if remSym:
							for sym in remSym:
								# ATTEMPT TO CONVERT KEYWORD TO ENCODE LANGUAGE 
								# try: 
								# except:
								if sym in subLine:
									if verbLog:
										Log.Debug(':: REMOVED %s FROM %s ::', sym, subLine)
									subLine = subLine.replace(sym, '')	
						# REMOVE SPACES BEFORE EACH SENTENCE
						subLine = subLine.strip()
						# REMOVE DASHES IN FRONT OF LINES
						if removeDashes:
							if subLine.startswith('-') or subLine.startswith(' '):
								# REMOVE FIRST APPEARANCE OF '-' AND/OR EMPTY SPACE FROM LINE
								cleanData += subLine[1:]+'\n'
							else:
								cleanData += subLine+'\n'
						else:
							cleanData += subLine+'\n'
			# BLOCK DONE :: RESET IGNORED STATE FOR NEXT BLOCK
			ignored = False

			# BLOCK DONE :: APPEND NEW LINE
			cleanData += '\n'

		# IF FORCED UTF-8 IS ENABLED
		if forceEnc:
			enc = 'UTF-8'

		# SAVE AS UTF-8 .SRT FILE
		with io.open(target, 'w+', encoding=enc, errors='replace') as subFile:
			subFile.write(cleanData)
		Log(':: SCRUBBED :: %s ::' % target.upper())
		Log('----------------------------------------------------------------------------------')
	else:
		Log('/!\ COULD NOT PROCESS :: %s /!\\', target)

####################################################################################################

# REGISTER AGENTS
class SubsCleanerAgentMovies(SubsCleanerAgent, Agent.Movies):
	agent_type_verbose = "Movies"

class SubsCleanerAgentTvShows(SubsCleanerAgent, Agent.TV_Shows):
	agent_type_verbose = "TV"