# Trello -> Toggl

A simple script for syncing Trello cards and Toggl projects.

Given a Trello organization and Toggl worskpace, `trello2toggl` will try to
match Trello boards and Toggl projects by name (identical string match), and
then sync cards and tasks between respective boards and projects.

For every open Trello card, a corresponding Toggl task is created, with
the prefix `[Trello #<cardId>]` and the card name (truncated to 50 characters).
When the card is archived, the corresponding Toggl task will be archived as
well.


## Quickstart

Download the script from GitHub:

    git clone https://github.com/dobarkod/trello2toggl.git
    cd trello2toggl

Prepare a Python virtual environment for it to run in:

    mkvirtualenv --no-site-packages trello2toggl
    pip install -r requirements.txt

Set up your API keys and configure sync parameters:

    cp run.py.sample run.py
    # now edit run.py to configure trello2toggl

Run it:

    ./run.py


## Tips

It can be a little scary running the sync on all your boards and toggls.
To try it out on a (test) project first, add the `project=['ProjectName']`
parameter to the `Sync` constructor in `run.py` to explicitly list the projects
that should be syncd (see the Sync dostrings for examples).

# License

Copyright (C) 2013. by Good Code.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
