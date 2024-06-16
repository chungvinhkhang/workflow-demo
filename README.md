# Demo steps

## 1. init db

```bash
python db.py
```

## 2. start workflow

```bash
python admin.py orientation
```

enter employee_id

## 3. check task list

```bash
python my_tasks.py $user_id list
```

## 4. finish first manual task

```bash
python my_tasks.py $user_id finish 1
```

## 5. finish non manual task by triggering simulated agent

```bash
python agent.py 2
```

recheck task list

```bash
python my_tasks.py $user_id list
```

## 6. finish the remaining manual task

```bash
python my_tasks.py $user_id finish 3
```

recheck task list

```bash
python my_tasks.py $user_id list
```
