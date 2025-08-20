
# myappmaker

Currently at an early stage of development, myappmaker (working title) aims to be a visual desktop app builder with features for both non-technical and technical users, including block coding and many more. Created and maintained by me, Kennedy R. S. Guerra ([Kennedy's GitHub][] | [Kennedy's website][]), it is based on the original design and ideas provided by William Adams ([William's GitHub][] | [William's website][]), who also closely oversees the project's design and development.

> [!CAUTION]
> Application at an early stage of development (MVP/alpha/prototype), missing many features and susceptible to crashing/malfunctioning or sudden requirement changes.

## Progress so far

Being at an early stage of development (MVP/alpha/prototype), myappmaker is receiving new features incrementally. In this section we'll highlight features as we add them. Keep in mind that these features might be changed, replaced or even removed since we are designing and developing it incrementally.


### Drawing recognition for widget insertion

Have you ever used pen and paper to sketch an app's interface? Well, in myappmaker you can scribble directly on the canvas and have your drawing replaced by the corresponding widget. Just hold the **Shift** key while drawing and release it once you are finished. Here's a demonstration:

![Drawing recognition demonstration](https://i.imgur.com/SNmOXm3.gif)

For now the widgets are very "default-looking", but in next iterations we intend to add custom looks, even a hand-drawn one.

You actually define the drawings you want to associate with each widget in the stroke settings dialog. Here's a demonstration:

![Setting drawings demonstration](https://i.imgur.com/oOiNsmM.gif)


## Installation/usage

To launch and use myappmaker you can either install it with `pip` or you can just download the source and launch myappmaker as a standalone/portable application (that is, without installing it).


### Installing myappmaker with pip

If you want to install it, just execute the command below. It will install myappmaker and also, if not available yet, [PySide6][], [shapely][] and [numpy][] (more precisely, shapely installs numpy automatically).

```
pip install --upgrade myappmaker
```

Depending on your system, you may need to replace `pip` with `pip3`.

If everything goes well, after installing you should be able to launch the app by typing `myappmaker` or `python -m myappmaker` in your command line (or `python3 -m myappmaker` depending on your system).


### Using myappmaker as a standalone/portable app (without installing it)

If you want to use myappmaker without installing it, you'll need 02 things:

- to have Python installed in your system along with [PySide6][], [shapely][] and [numpy][] (shapely automatically installs numpy for you);
- to download myappmaker's source (the `myappmaker` folder in the top level of this repository).

Then, to launch the app, you just need to go to the location where you put the `myappmaker` folder containing the source (not inside it), open the command line and run `python -m myappmaker` or `python3 -m myappmaker`, depending on your system.


## Troubleshooting

The usage of PySide6 may depend on the installation of extra components on your system. If you encounter problems to launch myappmaker, before assuming it is causing problems, first ensure that the problem isn't actually with the PySide6 installation. To do that, copy the PySide6 script below to your disk and execute it with the Python instance where you installed PySide6 (an empty window must appear):

```python
### simple_pyside6_app.py

### code originally found on
### https://www.pythonguis.com/tutorials/pyside6-creating-your-first-window/
### then slightly adapted for usage here

from PySide6.QtWidgets import QApplication, QWidget

import sys

app = QApplication(sys.argv)

window = QWidget()
window.show()

app.exec()
```

If an empty window does appear, then your PySide6 installation is OK. At this point, whichever problem you might be having with myappmaker is indeed, likely, within myappmaker, so the next step is to reach out to us as explained further ahead in the Issues sections (likely, you'll be using [GitHub discussions][]).

If the window didn't appear though, then I'm afraid you may need to install other PySide6 dependencies or fix something. Please, try pasting the error message on Google to look for a suitable solution for your system.


## Contributing

Everyone is welcome to suggest and contribute changes.

If the proposed change is small enough, you can submit your pull request for analysis right away and it will be answered ASAP.

Please, **submit pull requests (PRs) to the `develop` branch**, **NOT** to the `main` branch. This way it is easier/simpler for us to clean/refactor/improve submitted changes before ultimately merging them with `main`.


## Issues


### Urgent/critical issues

If you find a bug that...

- causes myappmaker to crash;
- representing something malfunctioning or not working at all;

...then, please, use [GitHub issues][] to submit an issue as soon as possible.

Please, include as much information as you can:

- your operating system;
- your Python version;
- what was your goal;
- the steps that resulted in the problem;
- screenshots/videos, if applicable.

Nevertheless, never hesitate to ask for help, even if you don't have much info about the problem or don't have any technical expertise.


### Minor issues

If however, the problem is not as serious/urgent, that is, it doesn't cause myappmaker to crash or malfunction, then, please, open a discussion on [GitHub discussions][] instead. There's a dedicated category for this kind of problem called "Minor issue".

It doesn't mean your issue is any less important. It is just that in myappmaker and other Indie Smiths repos we use [GitHub issues][] for things that crash the app or otherwise prevent the user from doing something that is supposed to be available (stuff that cause crashes or malfunctioning). When such a critical issue appears, any other work is paused and all attention is given to that issue so that it can be fixed ASAP.

This measure is taken for the benefit of the users: by doing things this way, whenever you have an urgent/critical issue, it won't compete for space with other less urgent matters. We'll be able to promptly schedule time to solve the issue.

Minor issues, suggestions of improvements, feature requests, feedback about bad experiences, etc. are all important, but they don't have the same urgency as something that crashes the app or causes it to malfunction. This is why we use [GitHub discussions][] for the less urgent stuff. They'll be tended to all the same, just not with the same urgency.

Of course, [GitHub discussions][] is used for many other important stuff as well, as we'll see in the next section.


## Discussions/forum

Consider [GitHub discussions][] as the official online forum for myappmaker.

It is used for many things like announcements to the community, to list planned/requested features, to communicate and discuss current work, etc.

If you have...

- feedback;
- suggestions;
- ideas;
- concerns;
- questions;
- constructive criticism;
- minor issues that don't cause the app to crash or malfunction;

...you are encouraged to post there.


## Contact

Contact me any time via [Bluesky][], [Twitter/X][] or [email][].

You are also welcome on the Indie Smiths's [discord server][].


## Patreon and donations

Please, support myappmaker and other useful apps of the Indie Smiths project by becoming our patron on [patreon][]. You can also make recurrent donations using [GitHub sponsors][], [liberapay][] or [Ko-fi][].

Both [GitHub sponsors][] and [Ko-fi][] also accept one-time donations.

Any amount is welcome and helps. Check the project's [donation page][] for all donation methods available.


## License

myappmaker's source is dedicated to the public domain with [The Unlicense][].



[Kennedy's GitHub]: https://github.com/KennedyRichard
[Kennedy's website]: https://kennedyrichard.com

[William's GitHub]: https://github.com/WillAdams
[William's website]: https://designinto3d.com/

[Bluesky]: https://bsky.app/profile/kennedyrichard.com
[Twitter/X]: https://x.com/KennedyRichard
[email]: mailto:kennedy@kennedyrichard.com
[discord server]: https://indiesmiths.com/discord

[patreon]: https://patreon.com/KennedyRichard
[GitHub sponsors]: https://github.com/sponsors/KennedyRichard
[liberapay]: https://liberapay.com/KennedyRichard
[Ko-fi]: https://ko-fi.com/kennedyrichard
[donation page]: https://indiesmiths.com/donate

[GitHub issues]: https://github.com/IndiePython/nodezator/issues
[GitHub discussions]: https://github.com/IndiePython/nodezator/discussions

[The Unlicense]: https://unlicense.org/

[PySide6]: https://doc.qt.io/qtforpython-6/
[shapely]: https://shapely.readthedocs.io/
[numpy]: https://numpy.org
