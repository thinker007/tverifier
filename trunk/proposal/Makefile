all: pdf

pdf:
	pdflatex paper.tex
	bibtex paper

	
	# twice to get references right the first time
	pdflatex paper.tex
	pdflatex paper.tex

clean:
	rm -f *.aux *.log *.bbl *.blg

upload:
	scp paper.pdf amusa@bert.cs.uic.edu:WWW/resources
