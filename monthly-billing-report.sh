#!/bin/bash
#
# Don't forget to configure your $HOME/.pgpass file for the authentication.!!!
#
# Copyright 2020 jbaten@i2rs.nl
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

width=80
dir=$(pwd)

read -e -p "Enter year : " -i "$(date +%Y)"  year
startmonth=$(date +%-m)
startmonth=$((startmonth-1))
read -e -p "Enter start month   : " -i "$startmonth"  startmonth

# arithmetic cast to and from decimal
endmonth=$(($startmonth+1))

# check for december
if [[ $(($startmonth)) -eq 12 ]]
then
    year2=$(($year+1))
    endmonth=1
else
    year2=$year
fi


read -e -p "Enter end month ($year2)   : " -i "$endmonth"  endmonth

startmonth=$(printf "%02d\n" ${startmonth})
endmonth=$(printf "%02d\n" ${endmonth})
echo "Generating report" > 2
echo "From: ${year}-${startmonth}-01" > 2
echo "To  : ${year2}-${endmonth}-01" > 2

today=$(date +"%F")

echo "Generating reports"

reportsdir=reports

organizations=$( psql -h 10.1.1.1 -U zammad zammad --tuples-only   -c "select o.name from organizations as o order by o.name asc " )

IFS=$'\n'

for organization in ${organizations}
do
  org=$( echo $organization | awk '{$1=$1};1' )
  echo -n "Doing: ${org}"
  # Determine number of results
  count=$( psql -h 10.1.1.1 -U zammad zammad --tuples-only  -c "select count(*)   \
     from organizations as o, tickets as t, ticket_articles as ta,  ticket_time_accountings as tm \
     where o.name = '${org}' and t.organization_id=o.id and ta.ticket_id=t.id and tm.ticket_article_id=ta.id  \
     and   date(ta.created_at) >= '${year}-${startmonth}-01' and   date(ta.created_at) <  '${year2}-${endmonth}-01' \
	 ;" ) 

  echo -n   "$count  "
  #count=$( expr $count + 0 )
  #echo $count

  if [[ $count -gt 0 ]]
  then

    reportfile=${reportsdir}/${org}-${year}-${startmonth}.html
    pdfreport=${reportsdir}/${org}-${year}-${startmonth}.pdf

	echo "$(pwd)/$reportfile"

  echo "<html><body>"                      > ${reportfile}  
	echo "<head>"    >>  ${reportfile}
	echo "<style>"    >>  ${reportfile}
	echo "td { white-space:nowrap; width: 1px; } " >>  ${reportfile}
	echo "</style>"    >>  ${reportfile}
	echo "</head>"    >>  ${reportfile}
	echo "<img src=${dir}/logo.png>"               >>  ${reportfile}
	echo "<h1>Monthly time billing report</h1>"          >>  ${reportfile}
	echo "Time period:<b>${year}-${startmonth}</b><br>"     >>  ${reportfile}
	echo "Organization:<b>${org}</b>"     >>  ${reportfile}
	echo "<p></p>"    >>  ${reportfile}
  
  echo "<h2>Ticket list summary</h2>" >>  ${reportfile}

  query="select  \
	  t.number as Ticket, \
		t.title as Title,
    concat( u.firstname,' ', u.lastname) as Name ,
	to_char(round(sum(tm.time_unit/60),2), 'FM99990.00') as Time, \
		  ( select string_agg( tag_items.name,', ') from tags, tag_items where  tags.o_id=t.id and tags.tag_item_id=tag_items.id)   as Tags \
		from organizations as o, tickets as t, ticket_articles as ta,  ticket_time_accountings as tm, users as u \
    	where o.name = '${org}' and t.organization_id=o.id and ta.ticket_id=t.id and tm.ticket_article_id=ta.id  \
    	and   date(ta.created_at) >= '${year}-${startmonth}-01' and   date(ta.created_at) <  '${year2}-${endmonth}-01' \
      and t.customer_id=u.id \
      group by t.id, t.number, t.title, u.firstname, u.lastname \
	  	order by t.number asc ;"

  #echo "$query" | tr '\n' ' ' | tr '\t' ' ' | sed -e 's/ \+/ /gp'

  psql -h 10.1.1.1 -U zammad zammad --html  -c "${query}"  >>  ${reportfile}


	# Totaal onderaan overzicht.
	# https://stackoverflow.com/questions/41457430/how-to-sum-all-columns-value-of-a-table-and-display-the-total-in-new-row-by-usin

	# TODO: check ta.internal = true/false?

  echo "<h2>Time spend overview</h2>" >>  ${reportfile}
  echo '<div style="overflow-x:auto;">' >>  ${reportfile}

        # old stuff left(regexp_replace(ta.body,E'<[^>]+>', '', 'gi'),${width}) as Text, \


  query="select  \
		coalesce(t.number, 'Total :') as Ticket, \
    to_char(ta.created_at,'DD-MON HH24:MI') as Date, \
    replace(  \
                ( \
                  case  \
                    when (length(ta.body)<=80 ) then left(regexp_replace(ta.body,E'<[^>]+>', '', 'gi'),${width}) \
                    else concat(left(regexp_replace(ta.body,E'<[^>]+>', '', 'gi'),${width}) ,'..>')  \
                  end ) 
      ,'<br />','') as Text, \
		  to_char(round(sum(tm.time_unit/60),2), 'FM99990.00') as Time \
		from organizations as o, tickets as t, ticket_articles as ta,  ticket_time_accountings as tm \
    	where o.name = '${org}' and t.organization_id=o.id and ta.ticket_id=t.id and tm.ticket_article_id=ta.id  \
    	and   date(ta.created_at) >= '${year}-${startmonth}-01' and   date(ta.created_at) <  '${year2}-${endmonth}-01' \
		group by grouping sets ( ( t.number, ta.created_at, ta.body, tm.time_unit),() ) 
	  	order by t.number asc , ta.created_at asc;"

  #echo "$query" | tr '\n' ' ' | tr '\t' ' ' | sed -e 's/ \+/ /gp'

	psql -h 10.1.1.1 -U zammad zammad --html  -c "${query}"  >>  ${reportfile}

    echo '</div>' >>  ${reportfile}
    echo '<div>' >>  ${reportfile}
  echo "========================================================="
	# convert to lowercase  echo "${a,,}"
	lcorg=${org,,}
        modfile="module-$lcorg.sh"

	# Is there for this organization a specific module to include here?
	if [ -f $modfile ]
	then
          read -p "Found $modfile. Should we run it? (y/N)" -i "N" antw
          if [[ ${antw:0:1} == "y" ]] || [[ ${antw:0:1} == "Y" ]]
          then
            # If yes, include and run it!
	    source $modfile
          fi
	fi

    echo '</div>' >>  ${reportfile}

    echo "</body></html>" >> ${reportfile}
	wkhtmltopdf ${reportfile} ${pdfreport}

  else
	echo -n -e "                                                      \r"

  fi
done

echo "Done!                                                       "


