import mmap
import sqlite3
import os
import datetime
from decimal import Decimal
import sys


cwd = os.getcwd()


class TopDomains():
    """Given a table 'mailing':

    CREATE TABLE mailing (
            addr VARCHAR(255) NOT NULL
    );
    
    The mailing table will initially be empty.  New addresses will be added
    on adaily basis.  It is expected that the table will store at least
    10,000,000 email addresses and 100,000 domains.
    
    Write a perl script that updates another table which holds a daily count
    of email addresses by their domain name.
    
    Use this table to report the top 50 domains by count sorted by percentage
    growth of the last 30 days compared to the total.
    
    ** NOTE **
    
    - The original mailing table should not be modified.
    
    - All processing must be done in Perl/PHP/Python/whatever language you
    are using (eg. no complex queries or sub-queries)
    
    - Submit a compressed file(tar/zip) with the files required to run your
    script.

    """
    
    def __init__(self, prev_days=30):
        self.prev_days = prev_days
        
    def read_domains(self):
        '''
        (Nonetype) -> dict
    
        Parse a csv .txt file containing a list of e-mails, strip anything
        before the @ and return the domain and the domains count
        '''
    
        all_domains = {}
        path = os.path.join(cwd, "emailData.txt")
        with open(path, 'r+b') as f:
            m = mmap.mmap(f.fileno(), 0) 
            while True:
                try:
                    line = m.readline().rstrip().decode("utf-8")
                    c = line.split(',')
                    d = str(c[0] + "," + c[1].split('@')[1])
                    if d not in all_domains:
                        all_domains[d] = 1
                    else:
                        all_domains[d] += 1
                except:
                    break
            m.close()
        return all_domains
    
    def get_domains(self, domain_dict, prev_days):
        '''
        (dict, int) -> (dict, dict, int, int)
    
        Parse dict created by read_domains() and return the current top 50
        domains, the top domains from 30 days ago, the current total domains 
        and the total domains from 30 days ago
        
        '''
    
        today = datetime.datetime.now()
        dd = datetime.timedelta(prev_days)
        earlier = today - dd
        current_top_50 = {}
        prev_top_50 = {}
    
        for key, value in domain_dict.items():
            c = key.split(',')
            if str(c[1]) not in current_top_50:
                current_top_50[str(c[1])] = value
            else:
                current_top_50[str(c[1])] += value
            if str(c[0]) <= str(earlier.strftime('%Y%m%d')):
                if str(c[1]) not in prev_top_50:
                    prev_top_50[str(c[1])] = value
                else:
                    prev_top_50[str(c[1])] += value
            else:
                continue
    
        top_50_domains = sorted(current_top_50.items(), key=lambda t: t[1],
                                reverse=True)
        del top_50_domains[50:]
    
        total_domains = sorted(prev_top_50.items(), key=lambda t: t[1],
                               reverse=True)
    
        return (top_50_domains, total_domains, sum(current_top_50.values()),
                sum(prev_top_50.values()))
    
    def save_data(self, curr_top_domains, prev_top_domains,
                  total_curr_domains, total_prev_domains, prev_days):
        """
        (dict, dict, int, int, int) -> Nonetype
    
        Save a .txt file to the current working directory displaying the top
        50 domains, ordered by percentage of growth between the number of
        days specified in prev_days
        
        """
        
        path = os.path.join(cwd, "Top50DomainData.txt")
        save_list = list()
        template = "{0:9}|{1:19}|{2:19}|{3:}"
        today = datetime.datetime.now().strftime('%Y/%m/%d')
        prev_date = (datetime.datetime.now() - 
                     datetime.timedelta(prev_days)).strftime('%Y/%m/%d')
        header = ("The top 50 domains by count. Ordered by percentage growth,"
                  " between {} and {} \n\n".format(today, prev_date))
    
        for curr_item in curr_top_domains:
            x = iter(prev_top_domains)
            try:
                while True:
                    prev_item = next(x)
                    if curr_item != prev_item:
                        continue
                    else:
                        calculation = "{0:.3f}".format((curr_item[1] / 
                                                        total_curr_domains) -
                                                       (prev_item[1] / 
                                                        total_prev_domains)
                                                       * 100)
                    save_list.append([calculation, curr_item[0], 
                                           curr_item[1], prev_item[1]])
                    break
            except StopIteration:
                calculation = "{0:.3f}".format((curr_item[1] /
                                                total_curr_domains)*100)
                save_list.append([calculation, curr_item[0],
                                       curr_item[1], prev_item[1]])
    
        save_list.sort(key=lambda t: Decimal(t[0]), reverse=True)
        str1 = template.format("% Changed", "Count on " + today,
                               "Count on " + prev_date, "Domain\n")

        for i in save_list:
            str1 += template.format(str(i[0]).rjust(7), str(i[2]).rjust(10),
                                    str(i[3]).rjust(10), i[1]) + "\n"
    
        with open(path, 'w') as w:
            w.write(header + str1)
        print(datetime.datetime.now().strftime("\n\n%I:%M:%S %p") + 
              " Top50DomainData.txt Completed - LOCATION: %s \n\n"
              %(path))
            
    def main(self):
        """
        Execute the main program
        """
        
        all_domains = self.read_domains()
        
        (curTopDomains, prevTopDomains, curDomainTotals, prevDomainTotal) \
            = self.get_domains(all_domains, self.prev_days)
        
        self.save_data(curTopDomains, prevTopDomains, curDomainTotals,
                       prevDomainTotal, self.prev_days)      

if __name__ == "__main__":

    current_version = (sys.version_info)
    if current_version < (3,0):
        print("This script requires python 3")
    else:
        print(datetime.datetime.now().strftime("%I:%M:%S %p") + 
              " Program starting...")
        TopDomains(30).main()
        print(datetime.datetime.now().strftime("%I:%M:%S %p") + 
              " Completed")
        