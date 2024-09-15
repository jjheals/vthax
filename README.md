# IntelOps

**Live deployment:** [intel-ops.us](https://intel-ops.us)

**Devpost:** [Link to Devpost](https://devpost.com/software/intelops-6rslyd)

## Authors

**Justin Healey (@jjheals)**

Justin is currently a student at Worcester Polytechnic Institute, pursuing B.S. Computer Science with a minor in INTL Global Studies, and a M.S. Cybersecurity, both expected in May 2025.

For two summers during college, he interned at Raytheon Technologies on their Enterprise cyber threat intelligence (CTI) team, and is looking to pursue a career in the same or similar field. 

[LinkedIn](https://www.linkedin.com/in/justin-healey-wpi/)

**Anay Gandhi (@anaygandhi)**

Anay is a third year student at the University of Massachusetts, Amherst, pursuing a double major in computer science and economics. 

[LinkedIn](https://www.linkedin.com/in/anaygandhi/)


## What it does

IntelOps is a platform that leverages a combination of optimization with machine learning and generative AI to assist analysts, commanders, officers, and other members of the armed forces and defense industrial base (DIB) in planning, executing, and improving military operations. 


## How we built it

IntelOps consists of three primary components:
- Frontend built with React
- Backend built with Python and Flask
- Cloud infrastructure hosted with Linode

## Challenges we ran into

Over the course of VTHacks-12, we had to overcome a few challenges: 
- [Computational limitations](#computational-limitations)
- [Time constraints](#time-constraints)
- [Git...](#git-naturally)

### Computational Limitations

The primary challenge we faced this weekend had to do with computational limitations. Our backgrounds are primarily in machine learning, but we did not have access to the amount of compute that we would need to do a lot of the things we originally wanted to.

For example, we spent a few hours trying to train a GPT model on more specialized documents relating to military strategy and history, such as Sun Tzu's *The Art of War*, scholarly articles, and historical fiction, but eventually we realized we simply were not going to be able to train a decent model on our Macbooks. It was at this point we decided to implement OpenAI's API and use ChatGPT for our model, which brings other challenges (taking user API keys as input, for example) and may sacrifice accuracy of a fine tuned or specialized model. 

### Time Constraints

You can achieve a lot in 36 hours (especially with enough redbull), but you can only achieve *so much*. Like most of the other teams, we were limited by the short time frame. 

### Git (naturally)

I don't think this needs much explaining. 

## Accomplishments that we're proud of

### Time Management & Discipline 

Throughout this weekend, we set timelines, goals, and deadlines for ourselves, and we were able to follow those deadlines, complete our work on time, and stick to doing what we were good at. We used our understanding of each other to create a plan and stuck to the plan.

### Improvement since our first ever hackathon (Fall 2022)

In Fall 2022, we went to North Carolina to compete in the Reinvent-the-wheel hackaton. We did not do well at this competition. We were, by most standards, ill-prepared and unexperienced.

This fall, we felt confident in our abilities; in mere hours we were able to acccomplish tasks that took us days just a few years earlier. Looking back on how far we have come as individuals is an incredibe feat.

## What we learned

### New libraries, modules, & technologies



### Practice working with complex data structures

This project required working with and structuring complex datatypes, including 3 to 4 dimensional arrays and dictionaries. We learned how to traverse these data structures and how to handle them efficiently on both the client and server side. 

### Full-stack development

This weekend, we learned about imlpementing all aspects of a project at both a technical and non-technical level, including about trade-offs in speed and efficiency for other features.

### Our ability to stay awake for nearly three straight days

This might be our most impressive feat all weekend.

## What's next for IntelOps

There was a lot we weren't able to accomplish this weekend that we would have liked to. Among these are: 

**Train and fine tune a more specialized GPT model** to give better recommendations, analysis, and overall more specific responses. The model could be trained on a corpus of documents relating to military strategy or historical military operations. Unfortunately we were unable to accomplish this due to computational efficiency and power constraints.

**Generate exportable formats for reports**, such as PDFs, HTML, or CSVs for raw data. The GPT's output combined with other ML techniques could generate a comprehensive mission plan with very little user interaction. 

**Create interactive visualizations** of the inner workings behind the predictions and recommendations. For the sake of simplicity, ease of use, and ease of understanding, a lot of the behind-the-scenes work of IntelOps is abstracted from the user's view. It would be cool to show some of these analyses, such as calculating the best path for a given set of vehicles and terrain. 