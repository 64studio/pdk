PDK has some excellent tools which we have refined over months of actual production work. It works well for us, making repositories and installable media. We feel that we are reasonable representatives of the general case. However, Linux distribution repositories and installer media tend to be filled with little hacks to solve local problems. From the beginning we've kept the pdk modules exposed to any python script, expecting that at some point someone will want to treat them as an API for doing odd things we couldn't have anticipated.

Essentially, we don't want to be a bottleneck. As much as possible we want to provide a fast flexible component model for handling thousands of packages, and allow you to do what you like with the results of processing.

So the API has always existed, and for most of it's life has had python docstrings explaining the parts.

Now we have a document included with PDK which shows through example scripts how to put the pieces of the api together to do some useful things. The scripts are verified to work each time we release PDK.

You should be able to read through the first example in 5 minutes and it might even solve an immediate problem for you.

So, without further ado, here's a link to The PDK API in 5 minutes. (http://trac.64studio.com/pdk/browser/doc/api-in-5min.fw)

For the most accurate information check the /usr/share/doc/pdk/ directory shipped with pdk package. 