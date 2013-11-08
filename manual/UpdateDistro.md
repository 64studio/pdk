A few QA guidelines to add new packages:

0) Make sure that the packages do actually install cleanly, by running
   the command:

   sudo apt-get install <all the packages I'm going to add>

   either on a clean distro installation or even better in a minimal
   chroot-ed base system created with pbuilder or cowbuilder

   This minimizes the chances of breaking the installer, because a
   single broken package results in the whole installer being broken.

1) Double check the package names you insert in the Makefile, in
   particular check the match the actual package you want to have
   and look for typos or misspelled words. The command:

   git diff

   will help you to focus on the changes you made.

   Also be careful when adding the "\" to the end of the line that now
   other character follows it, otherwise make will complain with a message like

   free@some-site.com:]/srv/pdk/projects/64studio/hardy $ make clean
   Makefile:64: *** commands commence before first target.  Stop.

2) Run

   make update

   to update the package lists for the repositories listed in etc/channels.xml,
   so that you won't get errors later (in case some of the newly inserted packages
   have different version in the local and remote lists)

3) Run

   make clean; make

   this will remove and rebuild the picax.xml and core.xml components, including
   the new packages and resolving dependences as needed.

4) Check if the dependency resolver did its job well by running:

   pdk semdiff picax.xml

   and make sure the changes you made don't do anything strange, like
   dropping some needed package because it conflicts with some of other
   package you just inserted. The output of the command might be long
   but have a look at it anyway, the DROP section is at the end.

5) Build the master repo and the iso:

   make master

   and check no errors are reported.

6) Commit your changes with a meaningful commit message:

   pdk commit -m "I did this and that"

   you can view the history with git log.

Done!

If you changed the version variable in the make file you might want to

make release

as well, the new images will be put in images/. However I'd suggest to
first test the generated master ISOs first. 

[How To](HowTo.md)
