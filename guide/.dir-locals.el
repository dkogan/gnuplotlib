;; I need some advices to be able to generate all the images. I'm not using the org
;; exporter to produce the html, but relying on github's limited org parser to
;; display everything. github's parser doesn't do the org export, so I must
;; pre-generate all the figures with (org-babel-execute-buffer) (C-c C-v C-b).

;; This requires advices to:

;; - Generate unique image filenames
;; - Communicate those filenames to Python
;; - Display code that produces an interactive plot (so that the readers can
;;   cut/paste the snippets), but run code that writes to the image that ends up in
;;   the documentation

;; There're some comments below, and a mailing list post:

;; https://lists.gnu.org/archive/html/emacs-orgmode/2020-03/msg00086.html

;; This triggered a bug/feature in emacs where the file-local eval was too big, and
;; wasn't happening automatically. Problem description:

;; https://lists.gnu.org/archive/html/emacs-devel/2020-03/msg00314.html
(( org-mode . ((eval .
  (progn
            (setq org-confirm-babel-evaluate nil)
            (org-babel-do-load-languages
             'org-babel-load-languages
              '((python  . t)
                (shell   . t)
                (gnuplot . t)))
  ;; This is all very convoluted. There are 3 different advices, commented in
  ;; place
  ;;
  ;; THIS advice makes all the org-babel parameters available to python in the
  ;; _org_babel_params dict. I care about _org_babel_params['_file'] specifically,
  ;; but everything is available
  (defun dima-org-babel-python-var-to-python (var)
    "Convert an elisp value to a python variable.
    Like the original, but supports (a . b) cells and symbols
  "
    (if (listp var)
        (if (listp (cdr var))
            (concat "[" (mapconcat #'org-babel-python-var-to-python var ", ") "]")
          (format "\"\"\"%s\"\"\"" var))
      (if (symbolp var)
          (format "\"\"\"%s\"\"\"" var)
        (if (eq var 'hline)
            org-babel-python-hline-to
          (format
           (if (and (stringp var) (string-match "[\n\r]" var)) "\"\"%S\"\"" "%S")
           (if (stringp var) (substring-no-properties var) var))))))
  (defun dima-alist-to-python-dict (alist)
    "Generates a string defining a python dict from the given alist"
    (let ((keyvalue-list
           (mapcar (lambda (x)
                     (format "%s = %s, "
                             (replace-regexp-in-string
                              "[^a-zA-Z0-9_]" "_"
                              (symbol-name (car x)))
                             (dima-org-babel-python-var-to-python (cdr x))))
                   alist)))
      (concat
       "dict( "
       (apply 'concat keyvalue-list)
       ")")))
  (defun dima-org-babel-python-pass-all-params (f params)
    (cons
     (concat
      "_org_babel_params = "
      (dima-alist-to-python-dict params))
     (funcall f params)))
  (unless
      (advice-member-p
       #'dima-org-babel-python-pass-all-params
       #'org-babel-variable-assignments:python)
    (advice-add
     #'org-babel-variable-assignments:python
     :around #'dima-org-babel-python-pass-all-params))
  ;; This sets a default :file tag, set to a unique filename. I want each demo to
  ;; produce an image, but I don't care what it is called. I omit the :file tag
  ;; completely, and this advice takes care of it
  (defun dima-org-babel-python-unique-plot-filename
      (f &optional arg info params)

    (let ((info-local (or info (org-babel-get-src-block-info t))))
      (if (and info-local
               (string= (car info-local) "python")
               (not (assq :file (caddr info-local))))
          ;; We're looking at a python block with no :file. Add a default :file
          (funcall f arg info
                   (cons (cons ':file
                               (format "guide-%d.svg"
                                       (condition-case nil
                                           (setq dima-unique-plot-number (1+ dima-unique-plot-number))
                                         (error (setq dima-unique-plot-number 0)))))
                         params))
        ;; already have a :file or not python. Just do the normal thing
        (funcall f arg info params))))

  (unless
      (advice-member-p
       #'dima-org-babel-python-unique-plot-filename
       #'org-babel-execute-src-block)
    (advice-add
     #'org-babel-execute-src-block
     :around #'dima-org-babel-python-unique-plot-filename))
  ;; If I'm regenerating ALL the plots, I start counting the plots from 0
  (defun dima-reset-unique-plot-number
      (&rest args)
      (setq dima-unique-plot-number 0))
  (unless
      (advice-member-p
       #'dima-reset-unique-plot-number
       #'org-babel-execute-buffer)
    (advice-add
     #'org-babel-execute-buffer
     :before #'dima-reset-unique-plot-number))
  ;; I'm using github to display guide.org, so I'm not using the "normal" org
  ;; exporter. I want the demo text to not contain the hardcopy= tags, but clearly
  ;; I need the hardcopy tag when generating the plots. I add some python to
  ;; override gnuplotlib.plot() to add the hardcopy tag somewhere where the reader
  ;; won't see it. But where to put this python override code? If I put it into an
  ;; org-babel block, it will be rendered, and the :export tags will be ignored,
  ;; since github doesn't respect those (probably). So I put the extra stuff into
  ;; an advice. Whew.
  (defun dima-org-babel-python-set-demo-output (f body params)
    (with-temp-buffer
      (insert body)
      (beginning-of-buffer)
      (when (search-forward "import gnuplotlib as gp" nil t)
        (end-of-line)
        (insert
         "\n"
         "if not hasattr(gp.gnuplotlib, 'orig_init'):\n"
         "    gp.gnuplotlib.orig_init = gp.gnuplotlib.__init__\n"
         "gp.gnuplotlib.__init__ = lambda self, *args, **kwargs: gp.gnuplotlib.orig_init(self, *args, hardcopy=_org_babel_params['_file'] if 'file' in _org_babel_params['_result_params'] else None, **kwargs)\n"))
      (setq body (buffer-substring-no-properties (point-min) (point-max))))
    (funcall f body params))

  (unless
      (advice-member-p
       #'dima-org-babel-python-set-demo-output
       #'org-babel-execute:python)
    (advice-add
     #'org-babel-execute:python
     :around #'dima-org-babel-python-set-demo-output))
  )))))

