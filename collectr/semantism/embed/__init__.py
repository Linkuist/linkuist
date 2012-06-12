import imp
import os

oembed = {}
module_dir = __package__.replace('.', '/')
for module_path in os.listdir(module_dir):
    if module_path.endswith(".py") and not module_path.startswith("__"):
        module_name = module_path.rstrip(".py")
        mod = imp.load_source(module_name, module_dir + os.sep + module_path)
        if not hasattr(mod, "get_host"):
            continue
        baseurl = mod.get_host()
        if isinstance(baseurl, basestring):
            baseurl = [baseurl]
        for url in baseurl:
            oembed[url] = mod

print oembed
