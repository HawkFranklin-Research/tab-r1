% file: hawkfranklin.cls
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{hawkfranklin}[2025/05/07 v1.5 HawkFranklin custom]

%%======== Base class and options ========
\RequirePackage{xifthen}
\newboolean{nonumbering}
\newboolean{address}
\newboolean{copyright}
\newboolean{confidential}
\DeclareOption{nonumbering}{\setboolean{nonumbering}{true}}
\DeclareOption{address}{\setboolean{address}{true}}
\DeclareOption{copyright}{\setboolean{copyright}{true}}
\DeclareOption{confidential}{\setboolean{confidential}{true}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{extarticle}}
\ProcessOptions
\LoadClass{extarticle}

%%======== Packages Required ========
\AtEndOfClass{\RequirePackage[tracking=smallcaps]{microtype}}
\RequirePackage[utf8]{inputenc}
\RequirePackage[english]{babel}
\RequirePackage{amsthm,amsmath,amsfonts,amssymb}
\RequirePackage{cmap}
\RequirePackage[T1]{fontenc}
\RequirePackage{url}
\RequirePackage[colorlinks=true,allcolors=blue]{hyperref}
\RequirePackage{pifont}
\RequirePackage[dvipsnames]{xcolor}
\RequirePackage{textcomp}
\RequirePackage[overload]{textcase}
\RequirePackage{graphicx}
\RequirePackage{colortbl}
\RequirePackage{booktabs}
\RequirePackage{longtable}
\RequirePackage{changepage}
\RequirePackage{enumitem}
  \setlist[itemize]{noitemsep}
  \setlist[enumerate]{noitemsep}
\RequirePackage{tabularx}
\RequirePackage{datetime}
\RequirePackage{fancyhdr}
\RequirePackage{lastpage}
\RequirePackage[explicit]{titlesec}
\RequirePackage{bibentry}
\RequirePackage{mdframed}
\RequirePackage{caption}
\RequirePackage{needspace}
\RequirePackage{soul}
\RequirePackage{kvoptions}
\RequirePackage{XCharter}
\RequirePackage[xcharter,bigdelims,vvarbb]{newtxmath}
\RequirePackage[scaled=1.1]{zlmtt}

%%======== Margins and column spacing ========
\RequirePackage[
  left=2.0cm,
  right=2.0cm,
  top=2.5cm,
  bottom=2.5cm,
  headheight=70pt,
  headsep=16pt,
  a4paper
]{geometry}

\setlength{\columnsep}{15pt}
\setlength{\parskip}{0.5\baselineskip}

%%======== Custom fonts ========
\newcommand{\watermarkfont}{\color{black50}\normalfont\fontsize{10}{12}\selectfont}
\newcommand{\headerfont}{\normalfont\sffamily\fontsize{8}{10}\selectfont}
\newcommand{\titlefont}{\color{black}\normalfont\bfseries\fontsize{21}{23}\selectfont}
\newcommand{\datesfont}{\normalfont\sffamily\itshape\fontsize{8}{10}\selectfont}
\newcommand\urlheaderfont{\color{blue}\fontsize{8}{10}\selectfont}
\newcommand{\absfont}{\bfseries\linespread{1.2}\fontsize{10}{12}\selectfont}
\newcommand{\keywordstitlefont}{\bfseries\linespread{1.2}\fontsize{8}{10}\selectfont}
\newcommand{\keywordsfont}{\itshape\linespread{1.2}\fontsize{11}{12}\selectfont}
\newcommand{\copyrightfont}{\normalfont\fontsize{7}{9}\selectfont}
\newcommand{\footerfont}{\color{black}\normalfont\fontsize{8}{10}\selectfont}
\newcommand{\subjectfont}{\color{white}\bfseries\fontsize{10}{12}\selectfont}
\newcommand{\headingfont}{\color{black}\bfseries\fontsize{13}{14}\selectfont}

%%======== Author & affiliation ========
\RequirePackage{authblk}
\setcounter{Maxaffil}{0}
\setlength{\affilsep}{0.2em}
\renewcommand\Authfont{\normalfont\bfseries\fontsize{9}{13}\selectfont}
\renewcommand\Affilfont{\normalfont\fontsize{8}{10}\selectfont}
\makeatletter
  \renewcommand\AB@affilsepx{, \protect\Affilfont}
\makeatother
\renewcommand\Authands{ and }

%%======== Company name and logo ========
\newcommand{\pafullname}{HawkFranklin Research}
\newcommand{\internalonly}{\hl{Confidential---Do not share or forward externally}}
\newcommand{\copyrightext}{\footerfont \textcopyright\,\the\year{} \pafullname. All rights reserved}

\newcommand{\keywords}[1]{\def\@keywords{#1}}
\newtoks\correspondingauthor
\newtoks\paperurl
\newtoks\reportnumber

%%======== Date format ========
\newdateformat{monthyeardate}{\THEYEAR-\twodigit{\THEMONTH}-\twodigit{\THEDAY}}

%%======== Section numbering ========
\setcounter{secnumdepth}{3}
\ifthenelse{\boolean{nonumbering}}{\setcounter{secnumdepth}{0}}{}

%%======== Header & footer setup ========
\pagestyle{fancy}
\fancyhf{} % Clear all

% Header for subsequent pages
\fancyhead[L]{%
  \hspace*{-2mm}\raisebox{-5pt}{\includegraphics[height=30pt]{assets/logo_with_name_HawkFranklin.png}}%
}
\makeatletter

\fancyhead[C]{%
  \makebox[\headwidth]{\hfill
    \begin{minipage}{0.6\headwidth}
      \centering \footerfont \@title
    \end{minipage}\hfill}}
      
\makeatother
\fancyhead[R]{%
  \footerfont\itshape\monthyeardate\today%
  %\ifthenelse{\boolean{confidential}}{\\\footerfont \internalonly}{}%
}
\fancyfoot[L]{%
  \ifthenelse{\boolean{confidential}}{\footerfont \internalonly}{\footerfont\bfseries\relax}
}
\fancyfoot[R]{\footerfont \thepage}
\renewcommand{\headrulewidth}{1pt}
\renewcommand{\footrulewidth}{1pt}
\let\DefaultHeadRule\headrule
\let\DefaultFootRule\footrule
\renewcommand{\headrule}{\color{gray}\DefaultHeadRule}
\renewcommand{\footrule}{\color{gray}\DefaultFootRule}

% First page header and footer
\fancypagestyle{firststyle}{%
  \fancyhf{}%
  \renewcommand{\headrulewidth}{0.6pt}
  \renewcommand{\headrule}{\color{gray}\DefaultHeadRule}
  \fancyhead[L]{%
    \hspace*{-2.5mm}\raisebox{-10pt}{\includegraphics[height=45pt]{assets/logo_with_name_HawkFranklin.png}}%
  }
  \fancyhead[R]{%
    \ifdefined\paperurl
      \if\relax\the\paperurl\relax\else
        \href{\the\paperurl}{\urlheaderfont \itshape \the\paperurl}\\\
      \fi
    \fi
    \footerfont\itshape\monthyeardate\today%
    \ifthenelse{\boolean{confidential}}{\\\footerfont \internalonly}{}%
  }
  \fancyfoot[L]{%
    \ifdefined\correspondingauthor
      \if\relax\the\correspondingauthor\relax\else
        \footerfont\itshape Corresponding author(s): \the\correspondingauthor\\
      \fi
    \fi
    \ifthenelse{\boolean{copyright}}{\copyrightext}{}%
  }
  \fancyfoot[R]{%
    \ifthenelse{\boolean{confidential}}{%
      \ifdefined\reportnumber
        \if\relax\the\reportnumber\relax\else
          \footerfont\itshape \pafullname{} Technical Report \the\reportnumber
        \fi
      \fi
    }{\footerfont\bfseries\relax}%
  }
  \renewcommand{\footrulewidth}{0pt}
}

%%======== Abstract environment ========
\renewenvironment{abstract}
  {\par\noindent\\\ignorespaces}
  {\par\bigskip}

%%======== Bibliography heading ========
\addto{\captionsenglish}{\renewcommand{\refname}{References}}
\newcommand{\citeas}[1]{\Needspace*{8\baselineskip}\noindent\bibentry{#1}}

%%======== Abstract & section formatting ========
\def\xabstract{abstract}
\long\def\abstract#1\end#2{%
  \def\two{#2}%
  \ifx\two\xabstract
    \long\gdef\theabstract{\ignorespaces#1}%
    \def\go{\end{abstract}}%
  \else
    \typeout{^^J^^J PLEASE DO NOT USE ANY \string\begin\space \string\end^^J
              COMMANDS WITHIN ABSTRACT^^J^^J}#1\end{#2}%
    \gdef\theabstract{\vskip12pt BADLY FORMED ABSTRACT: PLEASE DO
      NOT USE {\tt\string\begin...\string\end} COMMANDS WITHIN
      THE ABSTRACT\vskip12pt}%
    \let\go\relax%
  \fi
  \go}

\makeatletter
\newcommand{\abscontent}{%
  \noindent%
  \begingroup
    \absfont \theabstract
  \endgroup
  \@ifundefined{@keywords}{}{%
    \vskip1em \noindent \keywordsfont Keywords: \@keywords}%
}
\if@twocolumn%
\renewcommand{\maketitle}{%
  \twocolumn[%
    \begin{adjustwidth}{0pt}{24pt}
      \begin{flushleft}
        {\raggedright \titlefont \@title\par}%
        \vskip8pt
        {\raggedright \@author\par}%
        \vskip12pt
      \end{flushleft}
    \end{adjustwidth}
    \thispagestyle{firststyle}%
    \abscontent
    \vskip20pt
  ]
  \pagestyle{fancy}%
}
\else%
\renewcommand{\maketitle}{%
  \bgroup\setlength{\parindent}{0pt}%
    \begin{adjustwidth}{0pt}{24pt}
      \begin{flushleft}
        {\raggedright \titlefont \@title\par}%
        \vskip6pt
        {\raggedright \@author\par}%
        \vskip10pt
      \end{flushleft}
    \end{adjustwidth}
  \egroup
  \thispagestyle{firststyle}%
  \abscontent
  \pagestyle{fancy}%
}
\fi
\makeatother

%%======== Section formatting ========
\titleformat{\section}
  {\large\bfseries\headingfont}
  {\thesection.}
  {0.5em}
  {#1}
  []
\titleformat{name=\section,numberless}
  {\large\bfseries\headingfont}
  {}
  {0em}
  {#1}
  []
\titleformat{\subsection}
  {\bfseries}
  {\thesubsection.}
  {0.5em}
  {#1}
  []
\titleformat{\subsubsection}
  {\bfseries\itshape}
  {\thesubsubsection.}
  {0.5em}
  {#1}
  []
\titlespacing*{\section}{0pc}{3ex plus4pt minus3pt}{5pt}
\titlespacing*{\subsection}{0pc}{2.5ex plus3pt minus2pt}{2pt}
\titlespacing*{\subsubsection}{0pc}{2ex plus2.5pt minus1.5pt}{2pt}

%%======== Captions for Tables & Figures ========
\DeclareCaptionLabelSeparator{pipe}{ $\vert$ }
\captionsetup{%
  labelfont={},%
  labelsep=pipe,%
  figurename=Figure,%
  singlelinecheck=off%
}
