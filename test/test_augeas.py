import unittest
import sys
import os

__mydir = os.path.dirname(sys.argv[0])
if not os.path.isdir(__mydir):
    __mydir = os.getcwd()

sys.path.append(__mydir + "/..")

import augeas

MYROOT = __mydir + "/testroot"

def recurmatch(aug, path):
    if path:
        if path != "/":
            val = aug.get(path)
            if val:
                yield (path, val)

        m = []
        if path != "/":
            aug.match(path)
        for i in m:
            for x in recurmatch(aug, i):                
                yield x
        else:
            for i in aug.match(path + "/*"):
                for x in recurmatch(aug, i):
                    yield x

class TestAugeas(unittest.TestCase):
    def test01Get(self):
        "test aug_get"
        a = augeas.Augeas(root=MYROOT)
        self.failUnless(a.get("/wrong/path") == None)
        del a

    def test02Match(self):
        "test aug_match"
        a = augeas.Augeas(root=MYROOT)
        matches = a.match("/files/etc/hosts/*")
        self.failUnless(matches)
        for i in matches:
            for attr in a.match(i+"/*"):
                self.failUnless(a.get(attr) != None)
        del a

    def test03PrintAll(self):
        "print all tree elements"
        a = augeas.Augeas(root=MYROOT)
        path = "/"
        matches = recurmatch(a, path)
        for (p, attr) in matches:
            print >> sys.stderr, p, attr
            self.failUnless(p != None and attr != None)

    def test04Grub(self):
        "test default setting of grub entry"
        a = augeas.Augeas(root=MYROOT)
        num = 0
        for entry in a.match("/files/etc/grub.conf/title"):
            num += 1
        self.failUnless(num == 2)
        default = int(a.get("/files/etc/grub.conf/default"))
        self.failUnless(default == 0)
        a.set("/files/etc/grub.conf/default", str(1))
        a.save()
        default = int(a.get("/files/etc/grub.conf/default"))
        self.failUnless(default == 1)
        a.set("/files/etc/grub.conf/default", str(0))
        a.save()
    
    def test06SetMultiple(self):
        "Set multiple nodes at once"
        # Tests based on unit tests of aug_setm from augeas
        a = augeas.Augeas(root=MYROOT)
        #Change base nodes when SUB is None
        r = a.setm("/augeas/version/save/*", None, "changed")
        self.assertEquals(4, r)
        
        r = a.match("/augeas/version/save/*[. = 'changed']")
        self.assertEquals(4, len(r))
        
        # Only change existing nodes 
        r = a.setm("/augeas/version/save", "mode", "again")
        self.assertEquals(4, r)
        
        r = a.match("/augeas/version/save/*")
        self.assertEquals(4, len(r))
        
        r = a.match("/augeas/version/save/*[. = 'again']")
        self.assertEquals(4, len(r))
        
        # Create a new node 
        r = a.setm("/augeas/version/save", "mode[last() + 1]", "newmode")
        self.assertEquals(1, r)
        
        r = a.match("/augeas/version/save/*")
        self.assertEquals(5, len(r));
        
        r = a.match("/augeas/version/save/*[. = 'again']")
        self.assertEquals(4, len(r))
        
        r = a.match("/augeas/version/save/*[last()][. = 'newmode']")
        self.assertEquals(1, len(r))
        
        # Noexistent base 
        r = a.setm("/augeas/version/save[last()+1]", "mode", "newmode")
        self.assertEquals(0, r)
        
        # Invalid path expressions 
        self.assertRaises(ValueError, a.setm, "/augeas/version/save[]", "mode", "invalid")
        self.assertRaises(ValueError, a.setm, "/augeas/version/save/*", "mode[]", "invalid")
        

def getsuite():
    suite = unittest.TestSuite()
    suite = unittest.makeSuite(TestAugeas, 'test')
    return suite

if __name__ == "__main__":
    __testRunner = unittest.TextTestRunner(verbosity=2)
    __result = __testRunner.run(getsuite())
    sys.exit(not __result.wasSuccessful())

__author__ = "Harald Hoyer <harald@redhat.com>"
