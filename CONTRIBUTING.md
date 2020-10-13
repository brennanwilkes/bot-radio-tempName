# Workflow

### Large Features

1. Pull recent changes
```sh
git pull --all
```

2. Create new feature branch
```sh
git branch [FEATURE_NAME]
git checkout [FEATURE_NAME]
```
3. Work

4. Commit changes
```sh
git add -A
git commit -m "feat: [feature description]"
```

5. Repeat steps **3** and **4** until feature is complete

6. Retrieve recent commits.
```sh
git fetch --all
```

7. Merge feature branch
```sh
git checkout master
git merge --no-ff [FEATURE_NAME]
```

8. If merge conflicts, resolve them
    1. Search through all edited files for
    ```
    <<<<<<< HEAD
    blah blah blah #1
    =======
    blah blah blah #2
    >>>>>>> [FEATURE_NAME]
   ```
    2. Pick which `blah blah blah` line you want to keep, and delete the other
    3. Delete the `<<<`, `===`, and `>>>` lines

9. Push to GitHub
```sh
git push origin master
```

---

### Small Features

1. Pull recent changes
```sh
git pull --all
```

2. Work

3. Commit changes
```sh
git add -A
git commit -m "feat: [feature description]"
```

4. Pull even more recent changes
```sh
git pull origin master
```

5. Push to GitHub
```sh
git push origin master
```

6. If conflicts:
    1. Search through all edited files for
    ```
    <<<<<<< HEAD
    blah blah blah #1
    =======
    blah blah blah #2
    >>>>>>> [FEATURE_NAME]
   ```
    2. Pick which `blah blah blah` line you want to keep, and delete the other
    3. Delete the `<<<`, `===`, and `>>>` lines
    4. Push again
    ```sh
    git push origin master
    ```

