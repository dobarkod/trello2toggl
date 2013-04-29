from collections import defaultdict
import re
import time

from datetime import datetime
from iso8601.iso8601 import parse_date, Utc

from trello2toggl.trello import Trello
from trello2toggl.toggl import Toggl


class Sync(object):
    """Sync open Trello cards with Toggl tasks for same board/project."""

    def __init__(self, trello, toggl, trello_org_id, toggl_wid,
            projects=None):
        """Set up Trello to Toggl sync.

        Sync will be between identically named boards and projects (for
        example, cards from board named "Project X" will be synced with
        tasks from project named exactly the same, "Project X").

        The sync will happen only between boards/projects in the given
        Trello organization and Toggl workspace. Optionally, the sync may
        be further restricted by listing project names to sync explicitly
        in 'projects'.

        To run the sync once, see Sync.sync() method. To set up the continous
        sync, see the Sync.run() method.
        """

        self.trello = trello
        self.toggl = toggl

        self.filter_projects = projects
        self.trello_org_id = trello_org_id
        self.toggl_wid = int(toggl_wid)

        self.trello_boards = None
        self.trello_cards = None
        self.toggl_projects = None
        self.toggl_tasks = None
        self.to_create = None
        self.to_archive = None

        self.latest_action = datetime(1970, 1, 1, tzinfo=Utc())

    @staticmethod
    def parse_eta(txt):
        eta_tags = re.findall(r'\[eta [0-9.dh]+\]', txt)
        if len(eta_tags) == 0:
            return None
        try:
            return int(3600 * sum(float(x[:-1]) * (6 if x.endswith('d') else 1)
                for x in re.findall(r'[0-9.]+[dh]', eta_tags[0])))
        except:
            return None

    def get_trello_cards(self):
        if self.trello_org_id is None:
            raise ValueError('set trello org id first')

        self.trello_boards = self.trello.get_organization_boards(
            self.trello_org_id)

        # first, check if there are any new changes; if not, we can bail out
        # early
        latest_action = self.latest_action
        for b in self.trello_boards:
            if len(b.actions) > 0:
                d = parse_date(b.actions[0].date)
                if d > latest_action:
                    latest_action = d

        if latest_action <= self.latest_action:
            return self.latest_action

        self.trello_cards = defaultdict(dict)
        for b in self.trello_boards:
            for c in self.trello.get_board_cards(b.id, status='open'):
                self.trello_cards[b.name][c.idShort] = c

        return latest_action

    def get_toggl_tasks(self):
        if self.toggl_wid is None:
            raise ValueError('set toggl workspace id first')

        self.toggl_projects = self.toggl.get_workspace_projects(
            self.toggl_wid)
        pmap = dict((p.id, p) for p in self.toggl_projects)
        self.toggl_tasks = defaultdict(dict)
        p = re.compile(r'.* \(Trello #(\d+)\)$')
        p2 = re.compile(r'^\[Trello #(\d+)\] .*')

        for t in self.toggl.get_workspace_tasks(self.toggl_wid):
            m = p.match(t.name)
            if m:
                self.toggl_tasks[pmap[t.pid].name][int(m.group(1))] = t
            else:
                m = p2.match(t.name)
                if m:
                    self.toggl_tasks[pmap[t.pid].name][int(m.group(1))] = t

    def diff(self):
        if not self.trello_cards or not self.toggl_tasks:
            raise ValueError('cards/tasks not loaded')

        projects = (set(b.name for b in self.trello_boards) &
            set(p.name for p in self.toggl_projects))

        if self.filter_projects:
            projects &= set(self.filter_projects)

        self.to_create = set([])
        self.to_archive = set([])

        for p in projects:
            cards = self.trello_cards[p]
            tasks = self.toggl_tasks[p]

            # cards not yet having corresponding tasks
            self.to_create |= {(p, c) for c in cards.itervalues()
                if c.idShort not in tasks}

            # tasks not having corresponding cards any longer
            self.to_archive |= {t for (cid, t) in tasks.iteritems()
                if cid not in cards}

    def update_toggl(self):
        if self.to_create is None or self.to_archive is None:
            raise ValueError('create a diff first')

        pmap = dict((p.name, p.id) for p in self.toggl_projects)

        for p, c in self.to_create:
            cname = c.name if len(c.name) < 50 else c.name[:47] + '...'
            task_name = '[Trello #%d] %s' % (c.idShort, cname)
            print "  +", task_name
            self.toggl.create_task(task_name, pmap[p])

        for t in self.to_archive:
            print "  -", t.name
            self.toggl.mark_task_done(t.id)

    def sync(self):
        """Sync once"""

        def log(txt):
            print str(datetime.now()) + ": " + str(txt)

        log("getting new trello cards")
        latest_action = self.get_trello_cards()
        if latest_action > self.latest_action:
            log("got new actions, doing sync")
            log("getting toggl tasks")
            self.get_toggl_tasks()
            self.diff()
            log("updating toggl tasks")
            self.update_toggl()
            self.latest_action = latest_action
            log("sync done")

    def run(self, interval=1):
        """Run continuously (sync every 'interval' minutes) until stopped."""

        while True:
            self.sync()
            try:
                time.sleep(interval * 60)
            except KeyboardInterrupt:
                return
