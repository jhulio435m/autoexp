\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{expediente}[2025/02/18 Clase Profesional para Expedientes Tecnicos]

\LoadClass[11pt,a4paper]{article}

\RequirePackage[utf8]{inputenc}
\RequirePackage[spanish,es-tabla]{babel}
\RequirePackage[margin=2.5cm]{geometry}
\RequirePackage{titlesec}
\RequirePackage{fancyhdr}
\RequirePackage{graphicx}
\RequirePackage{helvet}
\RequirePackage{enumitem}
\RequirePackage{booktabs}
\RequirePackage{longtable}
\RequirePackage{array}
\RequirePackage{hyperref}

\renewcommand{\familydefault}{\sfdefault}

% Variables
\def\@entidad{ENTIDAD}
\def\@nombreproyecto{PROYECTO}
\def\@ubicacion{UBICACIÓN}
\def\@cui{0000000}
\def\@volumen{VOLUMEN}
\def\@consultor{CONSULTOR}
\def\@logoentidad{logo_placeholder.png}
\def\@logoconsultor{logo_placeholder.png}

\newcommand{\entidad}[1]{\def\@entidad{#1}}
\newcommand{\nombreproyecto}[1]{\def\@nombreproyecto{#1}}
\newcommand{\ubicacion}[1]{\def\@ubicacion{#1}}
\newcommand{\cui}[1]{\def\@cui{#1}}
\newcommand{\volumen}[1]{\def\@volumen{#1}}
\newcommand{\consultor}[1]{\def\@consultor{#1}}
\newcommand{\logoentidad}[1]{\def\@logoentidad{#1}}
\newcommand{\logoconsultor}[1]{\def\@logoconsultor{#1}}

% Formato de Secciones
\titleformat{\section}{\Large\bfseries\color{blue}}{\thesection}{1em}{}[\titlerule]
\titleformat{\subsection}{\large\bfseries}{\thesubsection}{1em}{}

% Encabezados
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small \@entidad}
\fancyhead[R]{\small \@volumen}
\fancyfoot[L]{\small CUI: \@cui}
\fancyfoot[R]{\thepage}

\newcommand{\hacerportada}{
    \begin{titlepage}
        \centering
        \begin{minipage}{0.45\textwidth}
            \centering \IfFileExists{\@logoentidad}{\includegraphics[height=2cm]{\@logoentidad}}{}
        \end{minipage}
        \hfill
        \begin{minipage}{0.45\textwidth}
            \centering \IfFileExists{\@logoconsultor}{\includegraphics[height=2cm]{\@logoconsultor}}{}
        \end{minipage}
        \vspace{2cm}
        
        {\Huge \bfseries \@entidad \par}
        \vspace{2cm}
        {\Large \bfseries \@volumen \par}
        \vspace{1.5cm}
        {\LARGE \bfseries PROYECTO: \par}
        \vspace{0.5cm}
        {\Large \@nombreproyecto \par}
        \vspace{2cm}
        {\large \textbf{UBICACIÓN:} \@ubicacion \par}
        {\large \textbf{CUI:} \@cui \par}
        \vfill
        {\large \textbf{CONSULTOR:} \par \@consultor \par}
        \vspace{1cm}
        {\large \today \par}
    \end{titlepage}
}
