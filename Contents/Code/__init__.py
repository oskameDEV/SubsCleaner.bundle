# -*- coding: utf-8 -*-
	#
		#
			# SUBS CLEANER :: AGENT FOR PLEX
				# BY [OK] KITSUNE.WORK - 2018
			# VERSION 0.91
		#
	#
#

# :: IMPORTS ::
from __future__ import with_statement
import sys
import os
import io
import re
import codecs

####################################################################################################

PLUGIN_VERSION = '0.91'

# :: USER CONFIGURED FILTERS ::
# CLEAN HTML FROM SUBTITLES
removeHTML 		= Prefs['removeHTML']

# REMOVE DASHES IN FRONT OF DIALOGUE. FOR EXAMPLE: "-Please, Izzi."
removeDashes 	= Prefs['removeDashes']

# FIX ALL-CAPS SUBTITLES (MAKES THEM NORMAL CAPITALIZED)
allCaps 		= Prefs['allCaps']

# FIX ALL-CAPS SUBTITLES (MAKES THEM NORMAL CAPITALIZED)
fixCaps 		= Prefs['fixCaps']

# :: TODO :: REMOVE SPECIFIC SYMBOLS FROM SENTENCES :: TODO ::
remSym 			= Prefs['remSym']
remSym 			= remSym.split(',')

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
customFilters 		= Prefs['customFilters']
customFilters		= customFilters.split(',')

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
	# LOCATION OF FILE
	target = folder+'/'+file
	# SET PERMISSIONS SO THAT FILE CAN ACTUALLY BE SAVED BY THE AGENT
	os.chmod(target, 0o777)

	# OPEN SUB FILE FOR SCRUBBING
	try:
		with io.open(target, 'r', encoding='UTF-8', errors='replace') as sourceFile:
			data 	= sourceFile.read()
			data 	= data.split('\n\n')
	except:
		Log(':: ERROR :: NOT UTF-8 ::')
		# sourceFile  = io.open(target, 'r')
		# # SAVE TO LIST
		# data 		= sourceFile.read()
		# data 		= data.split('\n\n')	# SPLIT DATA INTO SUBTITLE BLOCKS

	if data:
		# RESET VARS FOR EACH FILE
		cleanData 	= ''
		ignored 	= False
		
		# PROCESS BLOCK BY BLOCK
		for block in data:
			# PROCESS EVERY LINE
			for line in block.splitlines():
				subLine = line
				# REMOVE HTML TAGS FROM SUBTITLE
				if removeHTML:
					subLine = remHTML(line)
				# FIX SUBTITLES THAT ARE IN ALL CAPS
				if fixCaps:
					subLine = subLine.capitalize()

				# LEAVE INTACT IF LINE IS JUST A NUMBER OR TIMESTAMP
				if (subLine.isdigit()) or (re.match('\d{2}:\d{2}:\d{2}', subLine)):
					cleanData += subLine+'\n'

				# ELSE PROCESS SUBTITLE LINE AS SENTENCE
				else:
					# CHECK IF ANY PART OF THE TEXT IN BLOCK MATCHES FILTER LIST
					for line in block.splitlines():
						# CHECK TO SEE IF SENTENCE IN BLOCK CONTAINS A BLACKLISTED WORD
						for fltr in subFilters:
							if not ignored:
								if fltr.lower() in line.lower():
									# EXCEPTIONS
									if '..' not in line and '...' not in line:
										Log.Debug(':: IGNORING BLOCK BECAUSE OF {%s} FILTERED BY {%s} ::', line.upper(), fltr.upper())
										ignored = True # WILL NOT ADD THIS ENTIRE BLOCK
										cleanData += ' '

					# ELSE JUST PROCESS NORMALLY
					if not ignored:
						# REMOVE CERTAIN SYMBOLS FROM LINES BUT LEAVE THE REST INTACT
						if remSym:
							for sym in remSym:
								line = line.replace(sym, '')
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
						# REMOVE DASHES IN FRONT OF LINES
						if removeDashes:
							if subLine.startswith('-') or subLine.startswith(' '):
								# REMOVE FIRST APPEARANCE OF '-' AND/OR EMPTY SPACE FROM LINE
								cleanData += subLine[1:]+'\n'
							else:
								cleanData += subLine+'\n'
						else:
							cleanData += subLine+'\n'
			
			# BLOCK DONE :: APPEND NEW LINE
			cleanData += '\n'

			# BLOCK DONE :: RESET IGNORED STATE FOR NEXT BLOCK
			ignored = False

		#
		# :: TODO :: CLEAN UP EMPTY LINES AT END OF FILE :: TODO ::
		#

		# BLOCKS DONE :: CLOSE AND SAVE CURRENT FILE
		os.remove(target) # REMOVE ORIGINAL ENSURES CORRECT SAVING (AT LEAST ON MACOS)

		# SAVE AS UTF-8 .SRT FILE
		with codecs.open(target, "w", "utf-8-sig") as subFile:
			subFile.write(cleanData.encode('utf-8'))
		Log(':: SCRUBBED :: %s ::' % target.upper())

####################################################################################################

# REGISTER AGENTS
class SubsCleanerAgentMovies(SubsCleanerAgent, Agent.Movies):
	agent_type_verbose = "Movies"

class SubsCleanerAgentTvShows(SubsCleanerAgent, Agent.TV_Shows):
	agent_type_verbose = "TV"