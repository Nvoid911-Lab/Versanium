"""Real Clang warning gate for actual helpers; TLS ownership is an explicit double.

Uses the pinned real base::NoDestructor header. Full production TLS/header/target
compatibility still requires the separately authorized actual object compilation.
"""
from pathlib import Path
import argparse
import re
import subprocess
import tempfile
import unittest
from test_diagnostics import B,composed

PRELUDE=r'''
#include <array>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <iomanip>
#include <memory>
#include <mutex>
#include <pthread.h>
#include <sstream>
#include <string>
#include <thread>
#include <type_traits>
#include <vector>
#include "base/no_destructor.h"
std::atomic<bool> enabled{false};
std::atomic<int> owners{0},allocated{0},freed{0};
std::vector<std::string>* output=nullptr;std::mutex* output_lock=nullptr;
struct Sink : std::ostringstream {~Sink(){std::lock_guard<std::mutex> lock(*output_lock);output->push_back(str());}};
#define LOG(x) Sink()
namespace base {
class CommandLine {public:static bool InitializedForCurrentProcess(){return true;}
 static CommandLine* ForCurrentProcess(){static CommandLine c;return &c;}
 bool HasSwitch(const char*){return enabled.load();}};
struct TimeTicks {static TimeTicks Now(){return {};}TimeTicks since_origin(){return {};}
 int InMicroseconds(){return 7;}};
// API/ownership double using pthread TLS, matching Set(unique_ptr)/Get and
// delete-on-thread-exit. It is not a substitute for production base compilation.
template<class T>class ThreadLocalOwnedPointer {
 pthread_key_t key;
 static void Delete(void* p){delete static_cast<T*>(p);++freed;}
 public:ThreadLocalOwnedPointer(){assert(pthread_key_create(&key,&Delete)==0);++owners;}
 ~ThreadLocalOwnedPointer(){Set(nullptr);pthread_key_delete(key);}
 T* Get()const{return static_cast<T*>(pthread_getspecific(key));}
 std::unique_ptr<T> Set(std::unique_ptr<T> p){auto old=std::unique_ptr<T>(Get());
  if(p)++allocated;assert(pthread_setspecific(key,p.release())==0);return old;}
};
}
'''
MAIN=r'''
int main(){std::vector<std::string> log;std::mutex lock;output=&log;output_lock=&lock;
 auto emit=[](){CALLS};
 emit();assert(owners==0&&allocated==0&&log.empty());
 enabled=true;emit();assert(owners==6&&allocated==6&&log.size()==12);
 for(int batch=0;batch<5;batch++){
  std::vector<std::thread> threads;
  for(int i=0;i<4;i++)threads.emplace_back(emit);
  for(auto& thread:threads)thread.join();
  assert(allocated-freed==6);
 }
 assert(owners==6&&allocated==126&&freed==120&&log.size()==252);
 int first=0,second=0;
 for(const auto& line:log){first+=line.find("seq=1 ")!=std::string::npos;second+=line.find("seq=2 ")!=std::string::npos;}
 assert(first==126&&second==126);
 // Exact existing cap/idempotency behavior on a single module/scope.
 log.clear();for(int n=0;n<100;n++)module0::VSZoomLog("LIMIT","fixed",std::to_string(n));
 assert(log.size()==65&&log.back().find("event=DIAGNOSTIC_LIMIT")!=std::string::npos);
 assert(allocated-freed==6);
}
'''

class StorageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='zoomfs-storage-');cls.root=Path(cls.tmp.name)
        sources=composed(cls.root)
        cls.helpers=[]
        for path,s in sources.items():
            if path.endswith('.cc') and 'void VSZoomLog' in s:
                cls.helpers.append(re.search(r'bool VSZoomEnabled\(\).*?^}  // namespace',s,re.M|re.S).group().rsplit('}  // namespace',1)[0])
        assert len(cls.helpers)==6
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def compile(self,code,name):
        source=self.root/(name+'.cc');source.write_text(code)
        binary=self.root/name
        result=subprocess.run([str(ARGS.clang),'--std=c++20','-pthread','-Wall','-Wextra','-Werror','-Wexit-time-destructors','-I'+str(ARGS.chromium),str(source),'-o',str(binary)],capture_output=True,text=True)
        return result,binary
    def test_actual_helpers_gate_dedup_cap_thread_isolation_and_cleanup(self):
        self.assertTrue(all(h==self.helpers[0] for h in self.helpers))
        entry=re.search(r'struct Entry \{.*?\};',self.helpers[0],re.S).group()
        audit=entry+'\nstatic_assert(!std::is_trivially_destructible_v<Entry>);\nstatic_assert(!std::is_trivially_destructible_v<std::array<Entry,32>>);\nstatic_assert(std::is_trivially_destructible_v<base::NoDestructor<base::ThreadLocalOwnedPointer<std::array<Entry,32>>>>);\n'
        helpers=''.join('namespace module'+str(i)+'{\n'+h+'}\n' for i,h in enumerate(self.helpers))
        # Threads may interleave; assert per-thread sequence counts, not a
        # fictitious process-global ordering.
        calls=''.join('module'+str(i)+'::VSZoomLog("TEST","same","first");module'+str(i)+'::VSZoomLog("TEST","same","first");module'+str(i)+'::VSZoomLog("TEST","same","second");' for i in range(6))
        main=MAIN.replace('CALLS',calls)
        result,binary=self.compile(PRELUDE+audit+helpers+main,'actual_helpers')
        self.assertEqual(result.returncode,0,result.stderr)
        subprocess.run([str(binary)],check=True)
    def test_storage_only_change_preserves_exact_existing_evidence_logic(self):
        old=(B/'tests/fixtures/native-storage-before.cc.txt').read_text()
        storage='''  using Entries = std::array<Entry, 32>;
  static base::NoDestructor<base::ThreadLocalOwnedPointer<Entries>> storage;
  if (!storage->Get()) storage->Set(std::make_unique<Entries>());
  auto& entries = *storage->Get();'''
        for h in self.helpers:
            self.assertEqual(h.count(storage),1)
            self.assertEqual(h.replace(storage,'  static thread_local std::array<Entry, 32> entries;'),old)
    def test_real_clang_rejects_old_and_related_nontrivial_storage(self):
        for decl in ('static thread_local std::array<Entry,32> value;',
                     'static thread_local std::string value;',
                     'static std::vector<Entry> value;'):
            with self.subTest(declaration=decl):
                code='#include <array>\n#include <string>\n#include <vector>\nstruct Entry{std::string key,last;unsigned changes=0;};\nvoid f(){'+decl+'(void)value;}\nint main(){f();}\n'
                result,_=self.compile(code,'rejected_storage')
                self.assertNotEqual(result.returncode,0)
                self.assertIn('exit-time destructor',result.stderr)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--chromium',type=Path,required=True);p.add_argument('--clang',type=Path,required=True)
    ARGS,remaining=p.parse_known_args();unittest.main(argv=[__file__,*remaining])
