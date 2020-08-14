#! /usr/bin/env python3 
# baseballUpdates.py - Texts my phone live updates on the padres baseball game.

import bs4, time, textMyself, html5lib, getSchedule, datetime, re, teamSchedules, teamPages
import threading
import chromedriver_binary
from teamSchedules import teamSchedule
from teamPages import teamPage
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException

# TimeoutException thrown by 'presence_of_element_located' if there is no element.
# StaleElementReferenceException thrown if the page refreshes between 
# getting the element and 'get_attribute'.
# WebDriverException thrown if the page reaches an error (not loadable).

def getScheduleURL(team):
    """
    param team: the team to track.
    return: the URL to the team's schedule from
    https://www.cbssports.com/mlb/teams
    """
    return teamSchedule.get(team, None)

def getTeamURL(team):
    """
    param: the team to track.
    return: the URL to the team's homepage from
    https://www.mlb.com
    """
    return teamPage.get(team, None)

def launchBrowser(url):
    """
    This functions launches Chrome using selenium webdriver with the provided url.
    param url: the url to the team's homepage on mlb.com/[team]. 
    return: a WebDriver object.
    """
    browser = webdriver.Chrome()
    browser.implicitly_wait(30)
    browser.get(url)
    browser.maximize_window()
    return browser

def retryFindClick(browser, selector):
    """
    This function handles the StaleElementException.
    Attempts to locate the element by its css selector and click it.
    param browser: WebDriver object.
    param selector: css selector used to find the element on the website page.
    """
    maxAttempts = 3
    attempts = 0
    while attempts < maxAttempts:
        try:
            wait = WebDriverWait(browser, 10)
            elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            elem.click()
            return
        except TimeoutException:
            browser.close()
        except StaleElementReferenceException:
            pass
        attempts += 1

def retryFindInterceptedClick(browser, selector):
    """
    This function handles the StaleElementException.
    Attempts to locate the element by its css selector and click it.
    Used for elements that are not clickable because they are obscured by another element.
    param browser: WebDriver object.
    param selector: css selector used to find the obscured element on the 
    website page.
    """
    maxAttempts = 3
    attempts = 0
    while attempts < maxAttempts:
        try:
            wait = WebDriverWait(browser, 10)
            elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            webdriver.ActionChains(browser).move_to_element(elem).click(elem).perform()
            return
        except TimeoutException:
            browser.close()
        except StaleElementReferenceException:
            pass
        attempts += 1

def isTextPresent(browser, selector) -> str:
    """
    This function handles the StaleElementException.
    Attempts to locate the element by its css selector and retrieve its text.
    param browser: WebDriver object.
    param selector: css selector used to find the obscured element on the 
    website page.
    return: the text content from the element selected.
    """
    maxAttempts = 3
    attempts = 0
    while attempts < maxAttempts:
        try:
            wait = WebDriverWait(browser, 10)
            text_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            text = text_elem.get_attribute('textContent')
            break
        except TimeoutException:
            text = 'N/A'
            break
        except StaleElementReferenceException:
            pass
        attempts += 1
    return text

def getHomeTeam(browser) -> str:
    """
    This function gets the home team, locating the element with its css selector.
    param browser: WebDiver object.
    return: the home team.
    """
    selector = 'body tr.team-row.home span.short'
    try:
        wait = WebDriverWait(browser, 10)
        homeTeam_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        homeTeam = homeTeam_elem.get_attribute('textContent').strip().upper()
    except TimeoutException:
        homeTeam = 'N/A'
    except StaleElementReferenceException:
        homeTeam = isTextPresent(browser, selector).strip().upper()
    return homeTeam

def getAwayTeam(browser) -> str:
    """
    This function gets the away team, locating the element with its css selector.
    param browser: WebDiver object.
    return: the away team.
    """
    selector = 'body tr.team-row.away span.short'
    try:
        wait = WebDriverWait(browser, 10)
        awayTeam_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        awayTeam = awayTeam_elem.get_attribute('textContent').strip().upper()
    except TimeoutException:
        awayTeam = 'N/A'
    except StaleElementReferenceException:
        awayTeam = isTextPresent(browser, selector).strip().upper()
    return awayTeam

def getHomeRuns(browser) -> str:
    """
    This function gets the runs scored by the home team, locating the element with its css selector. 
    param browser: WebDiver object.
    return: runs scored by the home team.
    """
    selector = 'body tr.home td.score'
    try:
        wait = WebDriverWait(browser, 10)
        homeRuns_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        homeRuns = homeRuns_elem.get_attribute('textContent').strip().upper()
    except TimeoutException:
        homeRuns = 'N/A'
    except StaleElementReferenceException:
        homeRuns = isTextPresent(browser, selector).strip().upper()
    return homeRuns

def getAwayRuns(browser) -> str:
    """
    This function gets the runs scored by the away team, locating the element with its css selector. 
    param browser: WebDiver object.
    return: runs scored by the away team.
    """
    selector = 'body tr.away td.score'
    try:
        wait = WebDriverWait(browser, 10)
        awayRuns_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        awayRuns = awayRuns_elem.get_attribute('textContent').strip().upper()
    except TimeoutException:
        awayRuns = 'N/A'
    except StaleElementReferenceException:
        awayRuns = isTextPresent(browser, selector).strip().upper()
    return awayRuns

def getInning(browser) -> str:
    """
    This function gets the current inning, locating the element with its css selector. 
    param browser: WebDiver object.
    return: the current inning.
    """
    selector = '.show_default.spacer span.full'
    try:
        wait = WebDriverWait(browser, 10)
        inning_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector))) 
        inning = inning_elem.get_attribute('textContent').strip()
    except TimeoutException:
        inning = 'N/A'
    except StaleElementReferenceException:
        inning = isTextPresent(browser, selector).strip()
    return inning

# Returns the most recent play.
def getPlay(browser) -> str:
    """
    This function gets the most recent play, locating the element with its css selector. 
    param browser: WebDiver object.
    return: the current play.
    """
    selector = '.scoringPlays > section:last-of-type div.play:last-of-type p.description'
    try:
        wait = WebDriverWait(browser, 10)
        inningPlay_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        inningPlay = inningPlay_elem.get_attribute('textContent').strip()
    except TimeoutException:
        inningPlay = 'N/A'
    except StaleElementReferenceException:
        inningPlay = isTextPresent(browser, selector).strip()
    return re.sub(' +', ' ', inningPlay) # Cleans string, everything gets spaced equally.

def getPlayInning(browser) -> str:
    """
    # This function gets the inning of the most recent play, locating the 
    # element with its css selector. 
    # param browser: WebDiver object.
    # return: the current playInning.
    """
    selector = '.scoringPlays > section:last-of-type h2'
    try:
        wait = WebDriverWait(browser, 60)
        playInning_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        playInning = playInning_elem.get_attribute('textContent').strip().upper()
    except TimeoutException:
        playInning = 'N/A'
    except StaleElementReferenceException:
        playInning = isTextPresent(browser, selector).strip().upper()
    return playInning

def isInningOver(browser) -> bool:
    """
    This function checks to see if the innng is over.
    Return True in TimeoutException becuase the page is only visible during 
    the game. The only time we refresh to a new page where we can't find the
    element to tell us if the inning is at the end of the game.
    param browser: WebDriver object.
    return: True if the inning is over, False otherwise.
    """
    selector = 'div.matchup-status > div.matchup-progress-container > div > span:nth-child(1)'
    endRegex = re.compile(r'END')
    try:
        wait = WebDriverWait(browser, 10)
        inning_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        inning = inning_elem.get_attribute('textContent').upper()
        endMatch = endRegex.search(inning)
    except TimeoutException:
        return True
    except StaleElementReferenceException:
        inning = isTextPresent(browser, selector).upper()
        endMatch = endRegex.search(inning)
    if endMatch:
        return True
    return False

# Returns true if the game is over, false if it's not.
def isGameOver(inning, home_runs, away_runs) -> bool:
    """
    This function checks to see if the game is over. The page might not refresh
    to conclude the game is over, thus we need to manually check if it is.
    param inning: the current inning.
    param home_runs: the current runs scored by the home team.
    param away_runs: the current runs scored by the away team.
    return: True if the game is over, False otherwise. 
    """
    if inning.upper() == 'GAME OVER' or inning.upper() == 'FINAL':
        return True
    inningMatch = re.search(r'\d+', inning)
    if inningMatch:
        if int(inningMatch.group()) >= 9 and home_runs != away_runs:
            return True
    return False

def textPlay(homeTeam, home_runs, awayTeam, away_runs, playInning, play):
    """
    Texts the user the most recent play.
    param homeTeam: the home team.
    param home_runs: the current runs scored by the home team.
    param awayTeam: the away team.
    param awayRuns: the current runs scored by the away team.
    param playInning: the inning the play occurred.
    param: the play.
    """
    message = playInning + ': ' + play + '\n\n' + homeTeam + ': ' + home_runs + ' ' + awayTeam + ': ' + away_runs
    textMyself.textmyself(message)

def textInningScore(inning, homeTeam, home_runs, awayTeam, away_runs):
    """
    Texts the user the current score at the end of each inning.
    param inning: the inning that just ended.
    param homeTeam: the home team.
    param home_runs: the current runs scored by the home team.
    param awayTeam: the away team.
    param awayRuns: the current runs scored by the away team.
    """
    message = 'End ' + inning + ':\n' + homeTeam + ': ' + home_runs + ' ' + awayTeam + ': ' + away_runs
    textMyself.textmyself(message)

def textFinalScore(homeTeam, home_runs, awayTeam, away_runs):
    """
    Texts the user the final score at the end of the game.
    param homeTeam: the home team.
    param home_runs: the current runs scored by the home team.
    param awayTeam: the away team.
    param awayRuns: the current runs scored by the away team.
    """
    message = 'Final\n' + homeTeam + ': ' + home_runs + ' ' + awayTeam + ': ' + away_runs
    textMyself.textmyself(message)

def main():
    scheduleURL, teamURL = None, None
    while not scheduleURL and not teamURL:
        team = input('Enter a team to track (e.g. padres, yankees, etc.): ').strip().upper()
        scheduleURL = getScheduleURL(team)
        teamURL = getTeamURL(team)

    schedule = getSchedule.getShedule(scheduleURL)

    while schedule:
        currentDate = datetime.datetime.now()
        timeUntilStart = schedule[0] - currentDate

        # Sleep total time (seconds) until next game starts
        if timeUntilStart.total_seconds() > 0:
            print('Sleeping until next game starts...' + str(timeUntilStart.total_seconds()))
            time.sleep(timeUntilStart.total_seconds())

        browser = launchBrowser(teamURL)

        time.sleep(20) # Wait for pop up to go away

        # Check if the game is postponed.
        isPPDSelector = 'li.mlb-scores__list-item.mlb-scores__list-item--game:last-of-type \
div.g5-component--mlb-scores__MIG__versus--text'
        try:
            wait = WebDriverWait(browser, 10)
            isPPD_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, isPPDSelector))) 
            isPPD = isPPD_elem.get_attribute('textContent').strip().upper()
        except TimeoutException:
            isPPD = 'N/A'
        except StaleElementReferenceException:
            isPPD = isTextPresent(browser, isPPDSelector).strip().upper()
        
        if isPPD == 'PPD':
            continue

        # Selects and clicks 'Gameday' link
        gamedaySelector = 'div > div.g5-component--mlb-scores__button-group.g5-component--\
mlb-scores__button-group--primary > div > div.p-button.p-button--scores-gameday > a'
        try:
            wait = WebDriverWait(browser, 10)
            elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, gamedaySelector)))
            elem.click()
        except TimeoutException:
            browser.close()
        except StaleElementReferenceException:
            retryFindClick(browser, gamedaySelector)

        time.sleep(5) # Wait for page to load.

        # Selects and clicks 'PLAYS' tab. Had to select <li> tag because it obscured the <a> tag.
        playSelector = '#gameday-index-component__app > div > div:nth-child(5) > div > \
div:nth-child(3) > div > div > div > div > nav > ul > li:nth-child(2)'
        try:
            wait = WebDriverWait(browser, 10)
            elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, playSelector)))
            webdriver.ActionChains(browser).move_to_element(elem).click(elem).perform()
        except TimeoutException:
            browser.close()
        except StaleElementReferenceException:
            retryFindInterceptedClick(browser, playSelector)

        time.sleep(5) # Wait for page to load.

        startTime = schedule[0] # The time the game starts.
        totalTime = 0 # Keeps track of the total time the game has been going on.
        maxTime = 36000 # Games should not be longer than 10 hours (seconds).
        homeTeam, awayTeam = getHomeTeam(browser), getAwayTeam(browser)
        home_runs, away_runs = '0', '0'
        inning = getInning(browser)
        previousInning = None 
        plays = set() # Keeps track of the innings we've already processed.

        # Main loop of that provides updates of the game. Loop while there are innings in 
        # the game. totalTime is used to verify that we are not stuck in an infinite loop. 
        while inning or totalTime < maxTime:
            play = getPlay(browser)
            # If there is no play do nothing. If there is, check to see if its been processed.
            if play == 'N/A':
                pass
            else:
                if play not in plays:
                    playInning = getPlayInning(browser)
                    home_runs, away_runs = getHomeRuns(browser), getAwayRuns(browser)
                    thread = threading.Thread(target=textPlay, \
args=(homeTeam, home_runs, awayTeam, away_runs, playInning, play,))
                    thread.start()
                    thread.join()
                    plays.add(play)
            endOfInning = isInningOver(browser)

            # If the inning is over, check if the game is over and text the user the current score.
            if endOfInning:
                home_runs, away_runs = getHomeRuns(browser), getAwayRuns(browser)
                inning = getInning(browser)
                if inning != previousInning and inning != 'N/A':
                    gameOver = isGameOver(inning, home_runs, away_runs)
                    if gameOver:
                        thread = threading.Thread(target=textFinalScore, \
args=(homeTeam, home_runs, awayTeam, away_runs,))
                        thread.start()
                        thread.join()
                        break
                    thread = threading.Thread(target=textInningScore, \
args=(inning, homeTeam, home_runs, awayTeam, away_runs,))
                    thread.start()
                    thread.join()
                    previousInning = inning
                    time.sleep(180) # Sleep until next inning.
            try:
                browser.refresh()
            except WebDriverException:
                time.sleep(10)
                browser.refresh()
            time.sleep(10)
            totalTime = startTime - datetime.datetime.now()

        browser.close()
        del schedule[0]

if __name__ == '__main__':
    main()