Introduction
============

*zpaste* is a simple, single-user (or not-too-many-user)
pastebin/tinyurl hybrid, in case you want something a bit more
tweakable than the myriad of web services around.

Main selling points:

* Can specify `Content-Type:` to handle binaries somewhat.
* Does the job of both pastebin and tinyurl.
* Allow meaningful names as well as update/delete of past pastes.

Usage
=====

Paste the contents of standard input:

    $ ... | zpaste
    https://example.com/zpaste/wz9w

Give the paste link an optional ending:

    $ ... | zpaste --name=somename
    https://example.com/zpaste/somename

Upload a file:

    $ zpaste somefile.txt
    https://example.com/zpaste/somefile.txt

Upload a file, optionally give the link a different ending:

    $ zpaste --name=somename.txt somefile.txt
    https://example.com/zpaste/somename.txt

`zpaste` writes a link to the generated paste to standard output. The
optional argument passed with **--name** gives the ending of the link
(alphanumerics, dot, underscore and dash only); if not provided, a random name
or the passed file name is used.

Generate a redirect link:

    $ zpaste --link http://example.com/
    https://example.com/tiny/6lu9

Generate a redirect link, with an optional ending:

    $ zpaste --link http://example.com/ somename
    https://example.com/tiny/somename

This form generates a tinyurl-style address redirection link to the provided
URL and outputs it to stdout.

Delete an existing paste or redirect link:

    $ zpaste --del wz9w
    paste 'wz9w' deleted

    $ zpaste --del 6lu9
    link '6lu9' deleted

The *name* argument is required in this case.

Other command line options accepted by `zpaste`:

* **--force**: If specified, existing pastes/links are overwritten;
  otherwise, a duplicate name is an error.

Installation
============

Requirements
------------

You will need an Apache server, most likely one you can configure
freely.  Some bits of the system are done with `mod_rewrite`, and
others with `mod_alias`, and you'll also need `mod_cern_meta` loaded
for the content type specifying to work.  If your server is very
friendly with overrides, you may be able to get things rolling with
just suitable `.htaccess` files.

You will also need Perl, and the following heap of Perl modules.

The paste submission script needs `LWP`'s HTTP client, and if you want
to put the paste submission script behind HTTPS (you *really* should),
you'll need `IO::Socket::SSL` too (Debian/Ubuntu:
`libio-socket-ssl-perl`).

The server-side CGI script for accepting pastes needs a DBM library.
By default, `SDBM_File` (which is part of the core Perl distribution)
is used, but it is possible to use GDBM too.  In this case, though,
your Apache will need to be built with GDBM support.

The syntax-highlight support script needs the Perl interface of
[this](http://www.andre-simon.de/) syntax highlighting machine
(Debian/Ubuntu: `libhighlight-perl`).

Instructions
------------

The instructions here assume you will dedicate a single vhost for the
publicly accessible side, and stick the server-side paste accepting
script to another HTTPS-enabled vhost on the same server.  If your
setup differs from this, adapt accordingly.

### Step 1: decide where to put the stuff

You will need one data directory that is writable by the user/group
the server-side scripts run as.  This probably should not be under the
`DocumentRoot` of your server.  Let's call this directory *DATADIR*.
The default settings of the scripts use `/space/www/data/zpaste`.

You will also need to put the server-side script itself somewhere.
Let's call the absolute path to this script *SCRIPTPATH*.  By default,
this is in `/space/www/data/zpaste.cgi`.  This should be visible to
the world using the address *SCRIPTURL*; by default,
`https://example.com/zpaste.cgi`.

Finally, you will need to put the web server's document root
somewhere; let's call this directory *WEBDIR*.  The default value here
is `/space/www/zpaste`.  Make this directory accessible as *WEBURL*;
by default, `http://p.example.com/`.

### Step 2: edit the configuration sections of the scripts

In the command-line client **zpaste**, you will need to change:

* **KEY**: set to arbitrary string used for shared-secret authentication.
* **SCRIPT**: set to *SCRIPTURL* defined in Step 1.

In the server-side **zpaste.cgi**, you will need to change:

* **KEY**: set to the same arbitrary string as you did above.
* **DATADIR**: set to *DATADIR* of Step 1.
* **METADIR**: set to *DATADIR*/.web, unless you change `mod_cern_meta` configs.
* **METASUFFIX**: set to `.meta`, unless you change `mod_cern_meta` configs.
* **BASEURL**: set to *WEBURL* of Step 1.

Finally, in the highlight script **zpaste-hl.cgi**, you will need to change:

* **DATADIR**: set like in **zpaste.cgi**.
* **BASEURL**: set like in **zpaste.cgi**.
* **HL_LANGS**: set to highlight engine's language defs; default will work in Debian/Ubuntu.
* **HL_THEMES**: set to highlight engine's themes; default will work in Debian/Ubuntu.

### Step 3: putting stuff in place

Make the directories *DATADIR* and *DATADIR*/.web, and set their
permissions so that the server-side paste-accepting script can make
new files in both.

Put the edited **zpaste.cgi** to *SCRIPTPATH*.

Make the *WEBDIR* directory, set permissions so that the server can
read it.  Put some sort of `index.html` there if you want.  Make the
subdirectory *WEBDIR*/hl, and put the edited **zpaste-hl.cgi** there.

Put the edited **zpaste** to somewhere in your `$PATH`.

### Step 4: server configuration editing

Into the HTTPS-enabled vhost, put the line:

    ScriptAlias /zpaste.cgi *SCRIPTPATH*

If your *SCRIPTURL* has a subdirectory in it, remember to include that
in the first argument.

The *WEBURL* vhost (`p.example.com`) should look something like this;
substitute the correct paths to places marked {{LIKE THIS}}.

    <VirtualHost 1.2.3.4:80>
        ServerName p.example.com
        ServerAdmin webmaster@example.com
        ServerSignature On

        DocumentRoot {{WEBDIR}}

        RewriteEngine On
        RewriteMap zpastemap dbm=sdbm:{{DATADIR}}/rewrite.db
        RewriteCond %{REQUEST_URI} ^/([a-zA-Z0-9_-]+)$
        RewriteCond ${zpastemap:%1} !=""
        RewriteRule ^/([a-zA-Z0-9_-]+)$ ${zpastemap:$1} [L,R=302]
        RewriteRule ^/([a-zA-Z0-9_-]+)\.bin$ /$1 [PT,T=application/octet-stream]
        RewriteRule ^/([a-zA-Z0-9_-]+)\.([a-z0-9]+)$ /hl/zpaste-hl.cgi?name=$1&lang=$2 [NS,QSA]

        AliasMatch ^(/[a-zA-Z0-9_-]+)$ {{DATADIR}}$1

        <Directory {{WEBDIR}}>
            Order Allow,Deny
            Allow from all
        </Directory>

        <Directory {{WEBDIR}}/hl>
            SetHandler cgi-script
            Options ExecCGI
        </Directory>

        <Directory {{DATADIR}}>
            Order Allow,Deny
            Allow from all
            MetaFiles on
        </Directory>

        CustomLog /whatever/access.log combined
        ErrorLog /whatever/error.log
        LogLevel warn
    </VirtualHost>

Scripts
=======

This section is automatically generated from the script docs.

zpaste
------

### NAME

zpaste - zpaste client for sending paste requests

### SYNOPSIS

    ... | zpaste [opts] [name]
    zpaste --link http://www.example.com/ [name]

### DESCRIPTION

This scripts sends a paste request to the server-side CGI script
(**zpaste.cgi**).  Contents of the paste are read from standard input.
A link to the resulting paste is provided to standard output.

The optional name for the paste is provided as a regular command-line
argument.  The following command-line options are recognized:

* **--link** *URL*

> Instead of pasting the standard input contents, make a redirection
> entry to the URL provided as an argument to the --link option.  In
> this case, nothing is read from the standard input.

* **--force**

> If specified, existing pastes (or links) are overwritten.  If not, a
> duplicate name is an error.  Note that if you do not specify a name,
> this flag does nothing, as the randomly selected name is always chosen
> not to conflict with any existing entries.

* **--del**

> Instead of adding a new paste, only delete an existing one.  In this
> case, too, nothing is read from stdin.  The *name* argument is not
> optional if this flag is specified.

zpaste.cgi
----------

### NAME

zpaste.cgi - zpaste script for accepting paste requests

### SYNOPSIS

    https://www.example.com/zpaste.cgi (POST)

### DESCRIPTION

This scripts accepts a paste request from the command-line client
(**zpaste**).  The "form" submitted by **zpaste** has the following
fields:

* *key* (required)

> The pre-shared authentication key: an arbitrary string.  Just make
> sure the `KEY` constants in both this script and the **zpaste** client
> match.

* *data* (required, unless *del* is set)

> Contents of the paste.  In most cases, this should (and has to) be a
> file attachment field, the contents of which will be directly written
> as the contents of the paste.  The single exception is if *link* is
> set: in that case, this field needs to be a regular plain old text
> field, containing the URL to redirect to.

* *name* (optional, unless *del* is set)

> Name of the paste.  If not specified, a random name will be generated.

* *link* (optional, boolean)

> If set, the paste is instead a link to redirect to.

* *force* (optional, boolean)

> If set, a paste with the same name than an existing one overwrites the
> old one.  If not set, a duplicate name is an error.

* *del* (optional, boolean)

> If set, deletes the named paste instead of adding a new one.

zpaste-hl.cgi
-------------

### NAME

zpaste-hl.cgi - zpaste script for syntax highlighting

### SYNOPSIS

Visible URL:

    http://p.example.com/x.y[&theme=z&noln=1]

Underlying URL:

    http://p.example.com/zpaste-hl.cgi?name=x&lang=y \
      [&theme=z&noln=1]

### DESCRIPTION

This script is used to provide syntax highlighting for pastes.  The
script expects to be called via Apache rewriting module (as seen in
the **SYNOPSIS** section), and the URLs generated when user switches
languages or themes are written under this assumption.

The arguments accepted this script are the following:

* *name* (required)

> Name of the paste to syntax-highlight.

* *lang* (required)

> Language used for syntax-highlighting.

* *theme* (optional)

> Color theme.

* *noln* (optional)

> If set, omits the line numbers.
