# Repo: public_zammad_tools
My public repo with tools for the Zammad helpdesk ticketing software

In this repo I publish a few tools I created for the Zammad application that helps me in my daily business.
I am a full-time Linux and Open Source consultant and I sue Zammad a LOT!

What is in this repo?

- monthly-billing-report.sh. The name says it all. I use this every month when I bill my clients.
- weekly.sh. This app is started every morning to help me manage and focus on how I spend my time.

This file is the only documentation I provide. If you need support, you can email me and I will gladly make you an offer you can't refuse :-)

# monthly-billing-report.sh

When run it will first ask you for what year and what month you want the report to be created.
The 'end month' is the first month that is NOT included in the report.

For every organization in the Zammad database it will look and see if you spend some time working for them.
If so, it will generate a html file in the 'reports' subdirectory (not included in this repo, create it yourself).
This html file contains your company logo, a small header with organisation name and two lists.

The first list is a list of tickets you entered time on during the period entered.
The second list contains all the first lines of the articles, shopped of when they are too long and the time spend on that article.

## Installing

This script needs a configured .pgpass file in your home directory to be able to run.

# weekly.sh

Let's face it, I am sometimes chaotic, borderline ADD. Maybe I am ADD, I honestly don't know.
Recently I realised I needed a tool to help me focus on my work.
I wanted something that at day start would show my how I am doing workwise.
Basically an overview of the current week with the following information:
- Client name
- Some target I created with the amount of work I would like to do for this client in a week at a minimum.
- The amount I have worked for that particular client already in this week.
- And a bar graph showing me my progress towards my target.
- And the bar graph can have a color:
  - Red when there is a target but I'm not there yet, 
  - Green when I have passed my target \0/
  - Orange when there is no target defined.

After having used it for a couple if days I realised I also wanted to see the previous week.
Maybe last week I spend way more time on a client than targeted, so I could relax a little this week. Or, the opposite of course.

The application looks like this (client names have been obfuscated for obvious reasons):

![Screenshot of program](./weekly.png "Screenshot of program")

## Installing

To install this application you need a few things.
- The psycopg2 python driver for PostgreSQL
- The python tkinter gui library

Obviously you have to edit the weekly.conf configuration file.

The shell script also needs editing to get a good DISPLAY variable setting. My setting is probably not your setting.

Have fun!
Jeroen Baten
June 2020
