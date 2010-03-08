Installing tagnabbit
--------------------

Using python2.6, install 'virtualenv' and 'pip'.

Then::

 % python2.6 -m virtualenv ~/.env/tags
 % pip -E ~/.env/tags install jinja2 quixote==2.6 whoosh

Finally, ::

 % git clone http://github.com/ctb/tagnabbit.git

Running tagnabbit
-----------------

Activate the virtualenv (must be running bash)::

 % . ~/.env/tags/bin/activate

In the tagnabbit directory, run::

 % python2.6 -m tagnabbit.web -p 8000

to serve on port 8000, interface ''; or::

 % python2.6 -m tagnabbit.tests.run

to run the tests.

Other Documentation
-------------------

Whoosh query language for fulltext search:

  http://packages.python.org/Whoosh/querylang.html
