PDK's version control should be pretty easy to use. We've done our best to put a git-like face on pdk, so you should feel reasonably comfortable with it right away.

*First Steps*

To get started, you don't even need to set up a server, just start comitting within your workspace.

For instance, after you've built and resolved some components, you should add and commit them.


	
	pdk add yourdomain.com/acme.xml
	pdk commit
	


And you can do that all day.

Where did the commits go though? We use git under the covers, so committing to your local repository is the norm. When you are ready to share or publish your commits, you use the push command, assuming you have permission to do this...

	
	ssh elsewhere pdk workspace create /var/lib/projects/acme-project
	
	cat etc/channels.xml <<EOF
	<channels>
	  <elsewhere>
	    <type>source</type>
	    <path>file://elsewhere//home/you/acme-project</path>
	  </elsewhere>
	</channels>
	pdk push elsewhere
	


What happened is you just pushed your commits to the remote workspace. Note that this differs from cvs or svn commit. Instead of a single change set, you pushed multiple commits, the whole series.

Ok. So now what if another person wants to pick up where you left off?

They can set up their channels.xml file just like yours, then run:


	
	pdk pull elsewhere
	


This will work best in a fresh repository. As you and your development partner continue to work, you will push and pull series of commits quite a bit. Occasionally you will see an error admonishing you to pull before pushing. If you are out of date with the remote workspace, you need to pull its commits and merge them. This should feel familiar, much like the cvs commit update resolve-conflicts cycle you are used to. On the surface at least, it will feel like the same thing, except for the series of commits vs. single changeset mode of working.

*A Key Difference with Git under the Hood*

There was one major difference from cvs that took me awhile to grasp. When working with cvs, you cannot commit until you have successfully merged upstream changes. After doing some work, and before committing I would check to see if there were upstream changes I needed to think about merging. Then I went hunting for git commands similar to cvs update on a dirty repository. This never worked very well, as the git commands for merging all insisted on working with a clean repository, which does no good if you've done a bunch of work and want to commit.

After banging my head on this problem for some time, I figured out the answer. Just commit. Then pull. The merge we cvs-heads are used to doing right before committing comes after the commit in git, at merge time. So if you've done some work and anticipate having to update before committing, just commit. Then pull, which will require you to merge.

*Where Am I?*


	
	apt-get install gitk
	


This brings up a nice tool which graphically maps history, complete with parallel commits and merges.

*Tagging*

Pdk doesn't yet support tagging. See man git-tag for information on how to tag with git. The short version:


	
	git tag [tag-name] HEAD
	gitk
	


Gitk will show your tag.

*Composing Commit Messages*

Git treats the first line of a commit as the title for the commit. It shows up in gitk and gitweb in commit lists. So keep that in mind when you compose your commit message.

*Understanding Git*

We recommend that you spend a little time getting to know git, as understanding it may help you figure out how to back out of tricky situations when they arise.

    [Git Documentation] (http://www.kernel.org/pub/software/scm/git/docs/) 

Once you've been through that, keep in mind that the only pdk commands you must use are push and pull, to move cache files around. All the git commands for diffing, branching, merging, resetting, committing, and coordinating with others should work fine. Many of PDK's operations take place using an alternate index file, so you should be able to work unimpeded, even in tandem with pdk's commands. Keep in mind that pdk add does not invoke git add. So have fun.

[How To](HowTo.md)
