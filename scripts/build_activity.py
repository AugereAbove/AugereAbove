from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from html import escape
from html.parser import HTMLParser
import argparse
import calendar
import json
from pathlib import Path
import re
import subprocess
from urllib.request import Request, urlopen

PALETTE = ['#161f2d', '#17365c', '#22588d', '#3482c4', '#70bdff']
TEXT = '#e6edf3'
MUTED = '#9aa9bb'
BLUE = '#70bdff'

class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.counts = {}
        self.target = None
        self.buffer = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'td' and attrs.get('data-date') and attrs.get('id'):
            self.cells[attrs['id']] = attrs['data-date']
        if tag == 'tool-tip':
            self.target = attrs.get('for')
            self.buffer = []

    def handle_data(self, text):
        if self.target:
            self.buffer.append(text)

    def handle_endtag(self, tag):
        if tag != 'tool-tip' or not self.target:
            return
        label = ' '.join(''.join(self.buffer).split())
        match = re.match(r'^(No|[0-9,]+) contributions?\b', label)
        if match:
            count = 0 if match[1] == 'No' else int(match[1].replace(',', ''))
            self.counts[self.target] = count
        self.target = None
        self.buffer = []

def parse_calendar(html, start, end):
    parser = CalendarParser()
    parser.feed(html)
    days = {}
    for identifier, value in parser.cells.items():
        day = date.fromisoformat(value)
        if start <= day <= end:
            if identifier not in parser.counts:
                raise ValueError('A public calendar day is missing its contribution count')
            days[value] = parser.counts[identifier]
    expected = (end - start).days + 1
    if len(days) != expected:
        raise ValueError('Public contribution calendar did not cover the requested dates')
    return [{'date': day, 'count': count} for day, count in sorted(days.items())]

def public_repositories(user):
    repos = []
    for page in range(1, 101):
        result = subprocess.run(
            ['gh', 'api', f'users/{user}/repos?type=owner&per_page=100&page={page}'],
            capture_output=True, text=True, check=False,
        )
        if result.returncode:
            raise RuntimeError('GitHub repository query failed; check authentication or rate limits')
        batch = json.loads(result.stdout)
        if not isinstance(batch, list):
            raise ValueError('GitHub returned an invalid repository list')
        repos.extend(batch)
        if len(batch) < 100:
            return repos
    raise RuntimeError('Repository pagination exceeded the supported limit')

def aggregate(repos):
    public = [repo for repo in repos if not repo['private'] and not repo['fork']]
    languages = Counter(repo['language'] or 'Unclassified' for repo in public)
    return {
        'repositories': len(public),
        'stars': sum(repo['stargazers_count'] for repo in public),
        'forks': sum(repo['forks_count'] for repo in public),
        'languages': dict(sorted(languages.items(), key=lambda item: (-item[1], item[0]))),
    }

def label(x, y, text, size=14, color=TEXT, weight='400', anchor='start'):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(text))}</text>'

def card(width, height, title, description, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">'
        f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>'
        f'<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="14" fill="#0d1117" stroke="#303b4c"/>'
        f'<g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif">{body}</g></svg>\n'
    )

def activity_svg(snapshot):
    days = snapshot['days']
    start = date.fromisoformat(days[0]['date'])
    first = start - timedelta(days=(start.weekday() + 1) % 7)
    total = sum(day['count'] for day in days)
    active = sum(day['count'] > 0 for day in days)
    body = label(26, 33, 'PUBLIC CONTRIBUTION HISTORY', 15, BLUE, '600')
    body += label(26, 55, f'{start.year} to date | {active} active days', 12, MUTED)
    body += label(872, 35, f'{total} contributions', 18, TEXT, '600', 'end')
    columns = (date.fromisoformat(days[-1]['date']) - first).days // 7 + 1
    step = min(15, 790 / max(columns, 1))
    origin = 70
    previous_month = None
    for day in days:
        current = date.fromisoformat(day['date'])
        week = (current - first).days // 7
        weekday = (current.weekday() + 1) % 7
        x, y = origin + week * step, 82 + weekday * 15
        count = day['count']
        level = 0 if count == 0 else min(4, 1 + (count > 2) + (count > 5) + (count > 9))
        body += f'<rect x="{x:.1f}" y="{y}" width="11" height="11" rx="2" fill="{PALETTE[level]}"><title>{current}: {count} contributions</title></rect>'
        if current.month != previous_month:
            body += label(round(x, 1), 75, calendar.month_abbr[current.month], 10, MUTED)
            previous_month = current.month
    body += label(26, 107, 'Mon', 10, MUTED)
    body += label(26, 137, 'Wed', 10, MUTED)
    body += label(26, 167, 'Fri', 10, MUTED)
    body += label(26, 218, 'Source: public GitHub profile | refreshed ' + snapshot['as_of'], 11, MUTED)
    body += label(721, 218, 'Less', 10, MUTED)
    for index, color in enumerate(PALETTE):
        body += f'<rect x="{753+index*16}" y="207" width="11" height="11" rx="2" fill="{color}"/>'
    body += label(869, 218, 'More', 10, MUTED, anchor='end')
    return card(900, 240, 'AugereAbove public contribution history', f'{total} contributions visible on the public GitHub calendar in {start.year}.', body)

def monthly_svg(snapshot):
    months = defaultdict(int)
    for day in snapshot['days']:
        months[day['date'][:7]] += day['count']
    maximum = max(months.values(), default=0)
    total = sum(months.values())
    body = label(24, 32, 'PUBLIC ACTIVITY', 15, BLUE, '600')
    body += label(24, 55, f'{snapshot["as_of"][:4]} to date | {total} contributions', 13, MUTED)
    step = min(34, 390 / max(len(months), 1))
    for index, (month, count) in enumerate(sorted(months.items())):
        height = 95 * count / max(maximum, 1)
        x = 28 + index * step
        body += f'<rect x="{x:.1f}" y="{174-height:.1f}" width="21" height="{max(height, 2):.1f}" rx="3" fill="{BLUE if count else PALETTE[0]}"/>'
        body += label(round(x + 10, 1), 193, calendar.month_abbr[int(month[5:])], 10, MUTED, anchor='middle')
        if count:
            body += label(round(x + 10, 1), round(167-height, 1), count, 12, TEXT, anchor='middle')
    body += label(24, 221, 'Monthly totals from the public contribution calendar', 11, MUTED)
    return card(440, 242, 'Public contributions by month', 'Monthly aggregation of the same public calendar shown in the desktop chart.', body)

def overview_svg(snapshot):
    repo = snapshot['public_repositories']
    metrics = [('Public repos', repo['repositories']), ('Stars received', repo['stars']),
               ('Forks received', repo['forks']), ('Languages', len([name for name in repo['languages'] if name != 'Unclassified']))]
    body = label(24, 32, 'REPOSITORY OVERVIEW', 15, BLUE, '600')
    for index, (name, value) in enumerate(metrics):
        x, y = 26 + index % 2 * 212, 84 + index // 2 * 83
        body += label(x, y, value, 34, TEXT, '600')
        body += label(x, y+25, name, 13, MUTED)
    body += label(24, 236, 'Public, owned repositories | forks excluded', 11, MUTED)
    return card(440, 260, 'Public repository statistics', 'Repository totals, received stars and forks, and primary language count.', body)

def languages_svg(snapshot):
    languages = list(snapshot['public_repositories']['languages'].items())
    if len(languages) > 5:
        languages = languages[:4] + [('Other', sum(count for _, count in languages[4:]))]
    total = snapshot['public_repositories']['repositories']
    body = label(24, 32, 'REPOSITORIES BY LANGUAGE', 15, BLUE, '600')
    colors = {'Python': '#61afef', 'TypeScript': '#638fee', 'JavaScript': '#e9c958', 'Unclassified': '#68788c'}
    for index, (name, count) in enumerate(languages):
        y = 68 + index * 32
        body += label(24, y, name, 13, TEXT)
        body += label(414, y, f'{count} / {total}', 12, MUTED, anchor='end')
        body += f'<rect x="24" y="{y+8}" width="390" height="7" rx="3" fill="#1b2636"/>'
        body += f'<rect x="24" y="{y+8}" width="{390*count/max(total,1):.1f}" height="7" rx="3" fill="{colors.get(name, BLUE)}"/>'
    body += label(24, 236, 'Primary language per repo | not a skill score', 11, MUTED)
    return card(440, 260, 'Primary language by public repository', 'Each public nonfork repository is counted once. Unclassified means GitHub reports no primary language.', body)

def build(user, output):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}', user):
        raise ValueError('Invalid GitHub username')
    today = datetime.now(timezone.utc).date()
    start = date(today.year, 1, 1)
    url = f'https://github.com/users/{user}/contributions?from={start}&to={today}'
    request = Request(url, headers={'User-Agent': f'{user}-public-profile', 'Accept-Language': 'en-US'})
    with urlopen(request, timeout=30) as response:
        html = response.read(3_000_001)
    if len(html) > 3_000_000:
        raise ValueError('Public calendar response exceeded the limit')
    snapshot = {
        'user': user, 'as_of': str(today), 'scope': 'public_owned_nonfork_repositories_and_public_calendar',
        'sources': ['https://api.github.com/users/' + user + '/repos', url],
        'public_repositories': aggregate(public_repositories(user)),
        'days': parse_calendar(html.decode('utf-8'), start, today),
    }
    rendered = {
        'activity.svg': activity_svg(snapshot), 'activity-mobile.svg': monthly_svg(snapshot),
        'overview.svg': overview_svg(snapshot), 'languages.svg': languages_svg(snapshot),
        'snapshot.json': json.dumps(snapshot, indent=2) + '\n',
    }
    output.mkdir(parents=True, exist_ok=True)
    for name, content in rendered.items():
        temporary = output / (name + '.tmp')
        with temporary.open('w', encoding='utf-8', newline='\n') as output_file:
            output_file.write(content)
        temporary.replace(output / name)
    print(f'Generated public activity cards for {user}: {len(snapshot["days"])} calendar days, {snapshot["public_repositories"]["repositories"]} repositories')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', default='AugereAbove')
    parser.add_argument('--output', type=Path, default=Path('assets/activity'))
    args = parser.parse_args()
    build(args.user, args.output)
