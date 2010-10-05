
import os
import util
from mixxx import Feature
import SCons.Script as SCons


class MIDIScript(Feature):
    def description(self):
        return "MIDI Scripting"

    def enabled(self, build):
        build.flags['midiscript'] = util.get_flags(build.env, 'midiscript', 0)
        if int(build.flags['midiscript']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('midiscript', 'Set to 1 to enable MIDI Scripting support.', 1)

    def configure(self, build, conf):
        if not self.enabled(build):
            return
        if build.platform_is_windows:
            build.env.Append(LIBS = 'QtScript4')
	elif build.platform_is_linux:
            build.env.Append(LIBS = 'QtScript')
	elif build.platform_is_osx:
            # TODO(XXX) put in logic here to add a -framework QtScript
            pass
        build.env.Append(CPPPATH = '$QTDIR/include/QtScript')
	build.env.Append(CPPDEFINES = '__MIDISCRIPT__')

    def sources(self, build):
        return ["midi/midiscriptengine.cpp"]

class LADSPA(Feature):

    def description(self):
        return "Experimental LADSPA Support"

    def enabled(self, build):
        enabled = util.get_flags(build.env, 'ladspa', 0)
        build.flags['ladspa'] = enabled
        return True if int(enabled) else False

    def add_options(self, build, vars):
        vars.Add('ladspa', '(EXPERIMENTAL) Set to 1 to enable LADSPA plugin support', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return
        build.env.Append(CPPPATH=['#lib/ladspa'])
        build.env.Append(CPPDEFINES = '__LADSPA__')

    def sources(self, build):
        ladspa_plugins = SCons.SConscript(SCons.File('#lib/ladspa/SConscript'))
        #build.env.Alias('plugins', ladspa_plugins)
        sources = SCons.Split("""engine/engineladspa.cpp
                            ladspa/ladspaloader.cpp
                            ladspa/ladspalibrary.cpp
                            ladspa/ladspaplugin.cpp
                            ladspa/ladspainstance.cpp
                            ladspa/ladspacontrol.cpp
                            ladspa/ladspainstancestereo.cpp
                            ladspa/ladspainstancemono.cpp
                            ladspaview.cpp
                            ladspa/ladspapreset.cpp
                            ladspa/ladspapresetmanager.cpp
                            ladspa/ladspapresetknob.cpp
                            ladspa/ladspapresetinstance.cpp
                            dlgladspa.cpp
                            ladspa/ladspapresetslot.cpp
                            """)
        return ladspa_plugins + sources



class IPod(Feature):
    def description(self):
        return "NOT-WORKING iPod Support"

    def enabled(self, build):
        build.flags['ipod'] = util.get_flags(build.env, 'ipod', 0)
        if int(build.flags['ipod']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('ipod', 'Set to 1 to enable iPod support through libgpod', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return

        build.env.Append(CPPDEFINES = '__IPOD__')
        if build.platform_is_windows:
            build.env.Append(LIBS = 'gpod');
            # You must check v-this-v directory out from http://publicsvn.songbirdnest.com/vendor-binaries/trunk/windows-i686-msvc8/libgpod/
            build.env.Append(LIBPATH='../../../windows-i686-msvc8/libgpod/release/lib')
            # Following building the following must be added to the dist folder in order for mixxx to run with ipod support on Windows
            # \windows-i686-msvc8\libgpod\release\lib\libgpod.dll
            # \windows-i686-msvc8\glib\release\bin\libgobject-2.0-0.dll
            # \windows-i686-msvc8\glib\release\bin\libglib-2.0-0.dll
            # \windows-i686-msvc8\libiconv\release\bin\iconv.dll
            # \windows-i686-msvc8\gettext\release\binintl.dll
        if build.platform_is_linux or build.platform_is_osx:
            # env.Append(LIBS = 'libgpod-1.0')
            # env.Append(LIBS = 'glib-2.0')
            build.env.ParseConfig('pkg-config libgpod-1.0 --silence-errors --cflags --libs')
            build.env.ParseConfig('pkg-config glib-2.0 --silence-errors --cflags --libs')

    def sources(self, build):
        return ['wipodtracksmodel.cpp']

class MSVCDebug(Feature):
    def description(self):
        return "MSVC Debugging"

    def enabled(self, build):
        build.flags['msvcdebug'] = util.get_flags(build.env, 'msvcdebug', 0)
        if int(build.flags['msvcdebug']):
            return True
        return False

    def add_options(self, build, vars):
        if build.toolchain_is_msvs:
            vars.Add('msvcdebug', 'Set to 1 to link against MS libraries with debugging info (implies debug=1)', 0)

    def configure(self, build, conf):
        if self.enabled(build):
            if not build.toolchain_is_msvs:
                raise Exception("Error, msvcdebug flag set when toolchain is not MSVS.")

            # Enable debug multithread and DLL specific runtime methods. Required
            # for sndfile w/ flac support on windows.
            build.env.Append(CCFLAGS = '/MDd')
            build.env.Append(LINKFLAGS = '/DEBUG')
            if build.machine_is_64bit:
                build.env.Append(CXXFLAGS = '/Zi')
                build.env.Append(LINKFLAGS = '/NODEFAULTLIB:MSVCRT')
            else:
                build.env.Append(CXXFLAGS = '/ZI')
        elif build.toolchain_is_msvs:
            # Enable multithreaded and DLL specific runtime methods. Required
            # for sndfile w/ flac support on windows
            build.env.Append(CCFLAGS = '/MD')


class HifiEq(Feature):
    def description(self):
        return "High quality EQs"

    def enabled(self, build):
        build.flags['hifieq'] = util.get_flags(build.env, 'hifieq', 1)
        if int(build.flags['hifieq']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('hifieq', 'Set to 1 to enable high quality EQs', 1)

    def configure(self, build, conf):
        if not self.enabled(build):
            # Enables old crappy EQs
            build.env.Append(CPPDEFINES = ['__LOFI__', '__NO_INTTYPES__'])

class VinylControl(Feature):
    def description(self):
        return "Vinyl Control"

    def enabled(self, build):
        build.flags['vinylcontrol'] = util.get_flags(build.env, 'vinylcontrol', 1)
        if int(build.flags['vinylcontrol']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('vinylcontrol', 'Set to 1 to enable vinyl control support', 1)

    def configure(self, build, conf):
        if not self.enabled(build):
            return
        build.env.Append(CPPDEFINES = '__VINYLCONTROL__')
        build.env.Append(CPPPATH='#lib/xwax')
        build.env.Append(CPPPATH='#lib/scratchlib')

    def sources(self, build):
        sources = ['vinylcontrol.cpp',
                   'vinylcontrolproxy.cpp',
                   'vinylcontrolscratchlib.cpp',
                   'vinylcontrolxwax.cpp',
                   'dlgprefvinyl.cpp',
                   'vinylcontrolsignalwidget.cpp',
                   'engine/enginevinylcontrol.cpp',
                   '#lib/scratchlib/DAnalyse.cpp']
        if build.platform_is_windows:
            sources.append("#lib/xwax/timecoder_win32.c")
        else:
            sources.append("#lib/xwax/timecoder.c")
        return sources

class Tonal(Feature):
    def description(self):
        return "Tonal Audio Detection"

    def enabled(self, build):
        build.flags['tonal'] = util.get_flags(build.env, 'tonal', 0)
        if int(build.flags['tonal']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('tonal', 'Set to 1 to enable tonal analysis', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return

    def sources(self, build):
        sources = ['tonal/FourierTransform.cxx',
                   'tonal/Segmentation.cxx',
                   'tonal/tonalanalyser.cpp',
                   'tonal/ConstantQTransform.cxx',
                   'tonal/ConstantQFolder.cxx']
        return sources

class M4A(Feature):
    def description(self):
        return "Apple M4A audio file support"

    def enabled(self, build):
        build.flags['m4a'] = util.get_flags(build.env, 'm4a', 0)
        if int(build.flags['m4a']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('m4a', 'Set to 1 to enable building the Apple M4A support plugin.', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return

        have_mp4v2_h = conf.CheckHeader('mp4v2/mp4v2.h')
        have_mp4 = (have_mp4v2_h and conf.CheckLib(['mp4v2', 'libmp4v2'])) or conf.CheckLib('mp4')

        # We have to check for libfaad version 2.6 or 2.7. In libfaad
        # version 2.7, the type for the samplerate is unsigned long*,
        # while in 2.6 the type is uint32_t*. We can use the optional
        # call parameter to CheckLibWithHeader to build a test file to
        # check which one this faad.h supports.

        have_faad = conf.CheckLib(['faad', 'libfaad'])
        have_faad_26 = False

        # Check for libfaad version 2.6. This check doesn't work correctly on Windows
        # And we build it manually anyway, so we know it's v2.7
        if have_faad and not build.platform_is_windows:
            have_faad_26 = (not conf.CheckLibWithHeader(
                    'libfaad', 'faad.h', 'c++',
                    call = 'faacDecInit2(0, 0, 0, (unsigned long*)0, (unsigned char*)0);',
                    autoadd=False))

        if not have_mp4:
            raise Exception('Could not find libmp4v2 or the libmp4v2 development headers.')
        if not have_faad:
            raise Exception('Could not find libfaad or the libfaad development headers.')

        if have_faad_26:
            build.env.Append(CPPDEFINES = '__M4AHACK__')
            print "libfaad 2.6 compatibility mode... enabled"

        if have_mp4v2_h:
            build.env.Append(CPPDEFINES = '__MP4V2__')

        build.env.Append(CPPDEFINES = '__M4A__')
        build.env.Append(LIBS = 'libmp4v2')
        build.env.Append(LIBS = 'libfaad')


class WavPack(Feature):
    def description(self):
        return "WavPack audio file support"

    def enabled(self, build):
        build.flags['wv'] = util.get_flags(build.env, 'wv', 0)
        if int(build.flags['wv']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('wv', 'Set to 1 to enable building the WavPack support plugin.', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return
        have_wv = conf.CheckLib(['wavpack', 'wv'], autoadd=False)
        if not have_wv:
            raise Exception('Could not find libwavpack, libwv or its development headers.')


class ScriptStudio(Feature):
    def description(self):
        return "NOT-WORKING MixxxScript Studio"

    def enabled(self, build):
        build.flags['script'] = util.get_flags(build.env, 'script', 0)
        if int(build.flags['script']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('script', 'Set to 1 to enable MixxxScript/QtScript Studio support.', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return
	build.env.Append(CPPDEFINES = '__SCRIPT__')

    def sources(self, build):
        build.env.Uic4('script/scriptstudio.ui')
        return ['script/scriptengine.cpp',
                'script/scriptcontrolqueue.cpp',
                'script/scriptstudio.cpp',
                'script/scriptrecorder.cpp',
                'script/playinterface.cpp',
                'script/macro.cpp',
                'script/scriptcontrolevent.cpp',
                'script/trackcontrolevent.cpp',
                'script/numbercontrolevent.cpp',
                'script/numberrecorder.cpp',
                'script/macrolist.cpp',
                'script/trackrecorder.cpp',
                'script/sdatetime.cpp',
                'script/signalrecorder.cpp',
                'script/macrolistitem.cpp',
                'script/qtscriptinterface.cpp']




class Template(Feature):
    def description(self):
        return "TEMPLATE"
    def enabled(self, build):
        build.flags['TEMPLATE'] = util.get_flags(build.env, 'TEMPLATE', 0)
        if int(build.flags['TEMPLATE']):
            return True
        return False
    def add_options(self, build, vars):
        vars.Add('', '', 0)

class AsmLib(Feature):
    def description(self):
        return "Agner Fog\'s ASMLIB (http://www.agner.org/optimize)"

    def enabled(self, build):
        build.flags['asmlib'] = util.get_flags(build.env, 'asmlib', 0)
        if int(build.flags['asmlib']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('asmlib','Set to 1 to enable linking against Agner Fog\'s hand-optimized asmlib, found at http://www.agner.org/optimize/', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return

        build.env.Append(LIBPATH='#/../asmlib')
        if build.platform_is_linux:
		build.env.Append(CXXFLAGS = '-fno-builtin')   #Use ASMLIB's functions instead of the compiler's
		build.env.Append(LIBS = '":alibelf%so.a"' % build.bitwidth)
	elif build.platform_is_osx:
		build.env.Append(CXXFLAGS = '-fno-builtin')   #Use ASMLIB's functions instead of the compiler's
		build.env.Append(LIBS = '":alibmac%so.a"' % build.bitwidth)
	elif build.platform_is_windows:
		build.env.Append(CXXFLAGS = '/Oi-')   #Use ASMLIB's functions instead of the compiler's
		build.env.Append(LIBS = 'alibcof%so' % build.bitwidth)


class QDebug(Feature):
    def description(self):
        return "Debugging message output"

    def enabled(self, build):
        build.flags['qdebug'] = util.get_flags(build.env, 'qdebug', 0)
        if build.platform_is_windows:
            if int(build.flags['msvcdebug']):
                # Turn general debugging flag on too if msvcdebug is specified
		build.flags['qdebug'] = 1
        if int(build.flags['qdebug']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('qdebug', 'Set to 1 to enable verbose console debug output.', 1)

    def configure(self, build, conf):
        if not self.enabled(build):
            build.env.Append(CPPDEFINES = 'QT_NO_DEBUG_OUTPUT')

class CMetrics(Feature):
    def description(self):
        return "NOT-WORKING Community Metrics Stats-Reporting"

    def enabled(self, build):
        if build.platform_is_windows or build.platform_is_linux:
            build.flags['cmetrics'] = util.get_flags(build.env, 'cmetrics', 1)
        else:
            # Off on OS X for now...
            build.flags['cmetrics'] = util.get_flags(build.env, 'cmetrics', 0)
        if int(build.flags['cmetrics']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('cmetrics', 'Set to 1 to enable crash reporting/usage statistics via Case Metrics (This should be disabled on development builds)', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return

        build.env.Append(CPPDEFINES = '__C_METRICS__')

        if build.platform_is_windows:
            build.env.Append(LIBS = 'cmetrics')
	else:
            client = 'MIXXX'
            server = 'metrics.mixxx.org' # mixxx metrics collector
            SCons.Export('client server')
            build.env.Append(CPPPATH='#lib/cmetrics')

    def sources(self, build):
        return ['#lib/cmetrics/SConscript']

class MSVSHacks(Feature):
    """Visual Studio 2005 hacks (MSVS Express Edition users shouldn't enable
    this)"""

    def description(self):
        return "MSVS 2005 hacks"

    def enabled(self, build):
        build.flags['msvshacks'] = util.get_flags(build.env, 'msvshacks', 0)
        if int(build.flags['msvshacks']):
            return True
        return False

    def add_options(self, build, vars):
        if build.toolchain_is_msvs:
            vars.Add('msvshacks', 'Set to 1 to build properly with MS Visual Studio 2005 (Express users should leave this off)', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return
        build.env.Append(CPPDEFINES = '__MSVS2005__')

class Profiling(Feature):
    def description(self):
        return "gprof/Saturn profiling support"

    def enabled(self, build):
        build.flags['profiling'] = util.get_flags(build.env, 'profiling', 0)
        if int(build.flags['profiling']):
            if build.platform_is_linux or build.platform_is_osx or build.platform_is_bsd:
                return True
        return False

    def add_options(self, build, vars):
        if not build.platform_is_windows:
            vars.Add('profiling', '(DEVELOPER) Set to 1 to enable profiling using gprof (Linux) or Saturn (OS X)', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return
        if self.target_is_linux or self.target_is_bsd:
            build.env.Append(CCFLAGS = '-pg')
            build.env.Append(LINKFLAGS = '-pg')
        elif self.target_is_osx:
            build.env.Append(CCFLAGS = '-finstrument-functions')
            build.env.Append(LINKFLAGS = '-lSaturn')

class TestSuite(Feature):
    def description(self):
        return "Mixxx Test Suite"

    def enabled(self, build):
        build.flags['test'] = util.get_flags(build.env, 'test', 0) or \
            'test' in SCons.BUILD_TARGETS
        if int(build.flags['test']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('test', 'Set to 1 to build Mixxx test fixtures.', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return

        build.env.Append(LIBPATH="#lib/gtest-1.3.0/lib")
	build.env.Append(LIBS = 'gtest')
	build.env.Append(CPPPATH="#lib/gtest-1.3.0/include")

    def sources(self, build):
        gtest_dir = build.env.Dir("#lib/gtest-1.3.0")
        gtest_dir.addRepository(build.env.Dir('#lib/gtest-1.3.0'))
        #build.env['EXE_OUTPUT'] = '#/lib/gtest-1.3.0/bin'  # example, optional
	build.env['LIB_OUTPUT'] = '#/lib/gtest-1.3.0/lib'

        env = build.env
        SCons.Export('env')
        env.SConscript(env.File('scons/SConscript', gtest_dir))

class Shoutcast(Feature):
    def description(self):
        return "Shoutcast Broadcasting (OGG/MP3)"

    def enabled(self, build):
        build.flags['shoutcast'] = util.get_flags(build.env, 'shoutcast', 0)
        if int(build.flags['shoutcast']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('shoutcast', 'Set to 1 to enable shoutcast support', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return

        libshout_found = conf.CheckLib(['libshout','shout'])

        if not libshout_found:
            raise Exception('Could not find libshout or its development headers. Please install it or compile Mixxx without Shoutcast support using the shoutcast=0 flag.')

        vorbisenc_found = conf.CheckLib('vorbisenc')
        build.env.Append(CPPDEFINES = '__SHOUTCAST__')

        if build.platform_is_windows:
            build.env.Append(LIBS = 'pthreadVC2')
            build.env.Append(LIBS = 'pthreadVCE2')
            build.env.Append(LIBS = 'pthreadVSE2')
        elif not vorbisenc_found:
            # libvorbisenc does only exist on Linux and OSX, on Windows it is
            # included in vorbisfile.dll
            raise Exception("libvorbisenc was not found! Please install it or compile Mixxx without Shoutcast support using the shoutcast=0 flag.")

    def sources(self, build):
        build.env.Uic4('dlgprefshoutcastdlg.ui')
        return ['dlgprefshoutcast.cpp',
                'engine/engineshoutcast.cpp',
                'recording/encodervorbis.cpp',
                'recording/encodermp3.cpp']


class FFMPEG(Feature):
    def description(self):
        return "NOT-WORKING FFMPEG support"

    def enabled(self, build):
        build.flags['ffmpeg'] = util.get_flags(build.env, 'ffmpeg', 0)
        if int(build.flags['ffmpeg']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('ffmpeg', '(NOT-WORKING) Set to 1 to enable FFMPEG support', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return

        if build.platform_is_linux or build.platform_is_osx or build.platform_is_bsd:
            # Check for libavcodec, libavformat
            # I just randomly picked version numbers lower than mine for this - Albert
            if not conf.CheckForPKG('libavcodec', '51.20.0'):
                raise Exception('libavcodec not found.')
            if not conf.CheckForPKG('libavformat', '51.1.0'):
                raise Exception('libavcodec not found.')
            #Grabs the libs and cflags for ffmpeg
            build.env.ParseConfig('pkg-config libavcodec --silence-errors --cflags --libs')
            build.env.ParseConfig('pkg-config libavformat --silence-errors --cflags --libs')
            build.env.Append(CPPDEFINES = '__FFMPEGFILE__')
        else:
            # aptitude install libavcodec-dev libavformat-dev liba52-0.7.4-dev libdts-dev
            build.env.Append(LIBS = 'avcodec')
            build.env.Append(LIBS = 'avformat')
            build.env.Append(LIBS = 'z')
            build.env.Append(LIBS = 'a52')
            build.env.Append(LIBS = 'dts')
            build.env.Append(LIBS = 'gsm')
            build.env.Append(LIBS = 'dc1394_control')
            build.env.Append(LIBS = 'dl')
            build.env.Append(LIBS = 'vorbisenc')
            build.env.Append(LIBS = 'raw1394')
            build.env.Append(LIBS = 'avutil')
            build.env.Append(LIBS = 'vorbis')
            build.env.Append(LIBS = 'm')
            build.env.Append(LIBS = 'ogg')
            build.env.Append(CPPDEFINES = '__FFMPEGFILE__')

    def sources(self, build):
        return ['soundsourceffmpeg.cpp']
